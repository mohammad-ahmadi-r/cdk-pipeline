from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_efs as efs,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_rds as rds,
    aws_elasticloadbalancingv2 as elbv2,
    aws_autoscaling as autoscaling,
    aws_logs as logs,
    aws_datasync as datasync,
    aws_secretsmanager as sm
)
import aws_cdk as core
from constructs import Construct
import json

class WordpressStack(core.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "MyVpc", max_azs=2, cidr="10.0.0.0/16")

        my_bucket = s3.Bucket(self, 'MyBucket')
        
        ## Generate secret to use for Rds and Ecs
        secret = sm.Secret(
            self,
            'MyDatabaseCredentials',
            secret_name='mydatabase-credentials', 
            generate_secret_string=sm.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "admin"}),
                exclude_punctuation=True,
                include_space=False,
                password_length=16,
                generate_string_key='password'
            ),
            description='Credentials for MyDatabase'
        )

        ############# Setup RDS #############
        rds_security_group = ec2.SecurityGroup(self, 'MyRdsSecurityGroup',
                                               vpc=vpc,
                                               allow_all_outbound=True,
                                               security_group_name='my-rds-sg')
        ## Allow inbound traffic to RDS
        rds_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(3306))

        database = rds.DatabaseInstance(
            self, "MyDatabase",
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=vpc,
            multi_az=False,
            deletion_protection=False,
            allocated_storage=10,
            database_name="wordpressdb",
            security_groups=[rds_security_group],
            credentials=rds.Credentials.from_secret(secret) 
            )
        ## Allow access from within the VPC
        database.connections.allow_default_port_from(ec2.Peer.ipv4(vpc.vpc_cidr_block))

        ############# Setup File system ###########
        efs_security_group = ec2.SecurityGroup(self, 'MyEfsSecurityGroup',
                                               vpc=vpc,
                                               allow_all_outbound=True,
                                               security_group_name='my-efs-sg')

        ## Allow inbound traffic from ECS to the EFS on port 2049
        efs_security_group.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(2049))

        filesystem = efs.FileSystem(
            self, "MyEfsFileSystem",
            vpc=vpc,
            security_group=efs_security_group,
            encrypted=True,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING,
        )
        

        ############ Setup fargate ###########
        fargate_task_role = iam.Role(self, 'MyFargateTaskRole',
                                     assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'))

        ## IAM role to allow the task to access the RDS instance
        rds_access_policy = iam.PolicyStatement(effect=iam.Effect.ALLOW,
                                                actions=['rds-db:connect'],
                                                resources=[f"arn:aws:rds:{self.region}:{self.account}:{database.instance_identifier}"],
                                                conditions={'StringEquals': {'rds:DatabaseEngine': 'mysql'}})

        fargate_task_role.add_to_policy(rds_access_policy)

        
        ## task definition and cluster
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        task_definition = ecs.FargateTaskDefinition(
            self, "MyTaskDefinition",
            memory_limit_mib=512,
            cpu=256,
            task_role=fargate_task_role
        )
        
        ## Mount EFS to ECS
        efs_volume_configuration = ecs.EfsVolumeConfiguration(
            file_system_id=filesystem.file_system_id,
            root_directory="/",
            transit_encryption="ENABLED",
            transit_encryption_port=3049,
        )

        task_definition.add_volume(
            name="efs",
            efs_volume_configuration=efs_volume_configuration,
        )
        
        ## Create container
        container = task_definition.add_container(
            "MyContainer",
            image=ecs.ContainerImage.from_registry("wordpress"),
            port_mappings=[ecs.PortMapping(container_port=80)],
            environment={
                'RDS_PORT': '3306',
                'RDS_HOST': database.db_instance_endpoint_address,
                'S3_BUCKET_NAME': my_bucket.bucket_name
            },
            secrets={
                'RDS_USERNAME' : ecs.Secret.from_secrets_manager(secret, "username"),
                'RDS_USERNAME' : ecs.Secret.from_secrets_manager(secret, "password")
            },
            logging=ecs.LogDriver.aws_logs(
                stream_prefix='mycontainer',
                log_retention=logs.RetentionDays.ONE_MONTH
            )
        )


        container.add_mount_points(ecs.MountPoint(
            container_path="/var/www/html/wp-content",
            source_volume="efs",
            read_only=False,
        ))

        ## mount S3
        s3_mount_point = ecs.MountPoint(container_path='/var/www/html', read_only=False, source_volume='wordpress-data')
        container.add_mount_points(s3_mount_point)

        my_bucket.grant_read_write(container.task_definition.task_role)



        ## ECS permission to EFS
        execution_role = iam.Role(
            self, "MyExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonElasticFileSystemFullAccess")
            ],
        )

        task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["sts:AssumeRole"],
                resources=[execution_role.role_arn],
            )
        )


        ## ECS service
        fargate_security_group = ec2.SecurityGroup(self, 'MyFargateSecurityGroup',
                                                   vpc=vpc,
                                                   allow_all_outbound=False,
                                                   security_group_name='my-fargate-sg')
        fargate_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), 'Allow inbound traffic to Fargate service')

        fargate_security_group.add_egress_rule(efs_security_group, ec2.Port.tcp(2049), 'Allow outbound traffic from Fargate service to EFS')

        service = ecs.FargateService(
            self, "MyService",
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            security_groups=[fargate_security_group]

        )
        
        ############# Setup loadbalancer ###########

        alb = elbv2.ApplicationLoadBalancer(self, 'MyLoadBalancer', vpc=vpc, internet_facing=True)
        target_group = elbv2.ApplicationTargetGroup(self, 'MyTargetGroup', vpc=vpc, port=80, protocol=elbv2.ApplicationProtocol.HTTP)
        listener = alb.add_listener('MyListener', port=80)

        # Register target group with the listener
        listener.add_targets('MyTarget', port=80, targets=[service.load_balancer_target(
            container_name='MyContainer',
            container_port=80
        )])
