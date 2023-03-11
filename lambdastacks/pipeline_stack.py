from aws_cdk import (
    # Duration,
    Stack,
    #aws_lambda as _lambda
)
import aws_cdk as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct

from lambdastacks.pipeline_stage import PipelineStage
from aws_cdk.pipelines import ManualApprovalStep


class PipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pipeline= CodePipeline(self, "Pipeline", 
                pipeline_name="MyPipeline",
                synth=ShellStep("Synth", 
                    input=CodePipelineSource.git_hub("mohammad-ahmadi-r/cdk-pipeline", "main"),
                    commands=["npm install -g aws-cdk", 
                        "python -m pip install -r requirements.txt", 
                        "cdk synth"]
                )
            )
        
        testing_stage= pipeline.add_stage(PipelineStage(self, 'test',
            env=cdk.Environment(account="707597687992", region="eu-west-1")))

        testing_stage.add_post(ManualApprovalStep('approval'))

        #prod_stage= pipeline.add_stage(PipelineStage(self,"prod",
        #    env=cdk.Environment(account="707597687992", region="eu-west-1")))
 
