import aws_cdk as core
import aws_cdk.assertions as assertions

from v06_pipeine_v2.v06_pipeine_v2_stack import V06PipeineV2Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in v06_pipeine_v2/v06_pipeine_v2_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = V06PipeineV2Stack(app, "v06-pipeine-v2")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
