import aws_cdk as cdk
from constructs import Construct
from lambdastacks.lambda_stack import lambdaStack

class PipelineStage(cdk.Stage):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_stack= lambdaStack(self, "LambdaStack")
