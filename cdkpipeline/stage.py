import aws_cdk as cdk
from constructs import Construct
from . import  wordpress_stack

class PipelineStage(cdk.Stage):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stack= wordpress_stack.WordpressStack(self, "WordpressStack")
