import aws_cdk as cdk
from constructs import Construct
from cdkpipeline.wordpress_stack import WordpressStack

class PipelineStage(cdk.Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        mainStack = WordpressStack(self, "wordpressstack")
