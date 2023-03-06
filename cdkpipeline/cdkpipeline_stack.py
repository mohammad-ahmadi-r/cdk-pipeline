from aws_cdk import (
    Stack,
)
import aws_cdk as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct

class CdkpipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        CodePipeline(self, "Pipeline", 
                pipeline_name="MyPipeline",
                synth=ShellStep("Synth", 
                    input=CodePipelineSource.git_hub("mohammad-ahmadi-r/cdk-pipeline", "main"),
                    commands=["npm install -g aws-cdk", 
                        "python -m pip install -r requirements.txt", 
                        "cdk synth"]
                )
            )

