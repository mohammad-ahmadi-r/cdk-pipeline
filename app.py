#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdkpipeline.cdkpipeline_stack import CdkpipelineStack


app = cdk.App()
CdkpipelineStack(app, "CdkpipelineStack",
    env=cdk.Environment(account="707597687992", region="eu-west-1"))

app.synth()
