import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_lambda as _lambda

class lambdaStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_lambda = _lambda.Function(
            self, "MyLambdaFunction",
            code=_lambda.InlineCode("def lambda_handler(event, context):\n    return 'Hello, CDK!'"),
            handler="index.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_8
        )
