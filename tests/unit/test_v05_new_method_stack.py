import aws_cdk as core
import aws_cdk.assertions as assertions

from v05_new_method.v05_new_method_stack import V05NewMethodStack

# example tests. To run these tests, uncomment this file along with the example
# resource in v05_new_method/v05_new_method_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = V05NewMethodStack(app, "v05-new-method")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
