from aws_cdk import (
    aws_lambda as _lambda,
    core,
)

class MyLambdaCdkProjectStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the Lambda function
        my_lambda = _lambda.Function(
            self, "MyLambdaFunction",
            code=_lambda.Code.asset("lambda"),
            handler="handler.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_8,
        )
