#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdkstacks.pipeline_stack import PipelineStack


app = cdk.App()
PipelineStack(app, "PipelineStack",
    env=cdk.Environment(account='707597687992', region='eu-west-1'))

app.synth()
