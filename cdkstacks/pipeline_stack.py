from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_secretsmanager as secrets
)

import aws_cdk as cdk
from constructs import Construct

class PipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        #my_secret = secrets.Secret.from_secret_arn(self, 'MySecret', f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:{github-token}")
        #secret_value = my_secret.secret_value.to_string()
        
        #secret = secrets.Secret.from_secret_attributes(self, "ImportedSecret",
         # secret_complete_arn="arn:aws:secretsmanager:{self.region}:{self.account}:secret:{github-token}",
          # If the secret is encrypted using a KMS-hosted CMK, either import or reference that key:
          # encryption_key=....
        #)
        # Create the source and build actions
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="Source",
            owner="mohammad-ahmadi-r",
            repo="cdk-pipeline",
            branch="main",
            oauth_token= cdk.SecretValue.secrets_manager('github-token'),
            output=source_output
        )
        '''
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            project="cdkpipeline",
            input=source_output,
            outputs=[codepipeline.Artifact()],
        )'''

        # Create the manual approval action
        approval_action = codepipeline_actions.ManualApprovalAction(
            action_name="Approval"
        )

        # Add the actions to the pipeline stages
        pipeline = codepipeline.Pipeline(self, "MyPipeline", pipeline_name="my-pipeline", stages=[
            codepipeline.StageProps(
                stage_name="Source",
                actions=[source_action]
            ),
            codepipeline.StageProps(
                stage_name="Approval",
                actions=[approval_action]
            )
        ])

