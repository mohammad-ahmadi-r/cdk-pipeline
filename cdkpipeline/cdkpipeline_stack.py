from aws_cdk import (
    Stack,
)
import aws_cdk as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep, ManualApprovalStep
from constructs import Construct
#from . import stage

class CdkpipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pipeline= CodePipeline(self, "Pipeline", 
                pipeline_name="MyPipeline",
                synth=ShellStep("Synth", 
                    input=CodePipelineSource.git_hub("mohammad-ahmadi-r/cdk-pipeline", "main"),
                    commands=["npm install -g aws-cdk", 
                                "python -m pip install -r requirements.txt", 
                                "cdk synth"]
                    #commands=["npm ci", "npm run build", "npx cdk synth"]
                )
            )
'''
        test_stage= pipeline.add_stage(stage.PipelineStage(self,"test",
            env=cdk.Environment(account="707597687992", region="eu-west-1")))
        test_stage.add_post(ManualApprovalStep('approval'))

        prod_stage= pipeline.add_stage(stage.PipelineStage(self,"prod",
        env=cdk.Environment(account="707597687992", region="eu-west-1")))
'''
