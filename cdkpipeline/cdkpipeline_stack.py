from aws_cdk import (
    Stack,
)
import aws_cdk as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct

from wordpress_stack import WordpressStack
from wordpress_test_stack import WordpressTestStack

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
                )
            )

        test_stage= pipeline.add_stage(WordpresTestStack(self, "test"))
        test_stage.add_post(ManualApprovalStep('approval'))

        prod_stage= pipeline.add_stage(WordpressStack(self, "prod"))
