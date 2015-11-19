# Project Whimbrel

## AWS Decentralized Workflow

Whimbrel is a workflow toolkit for designed around not having any centralized server,
and instead uses the AWS services to eliminate the cost of running one (or multiple)
servers to handle workflow.

DynamoDB (the AWS NoSQL database) coordinates the activity status, while activity
triggers come from the activities themselves, or from external sources.

As a result of this, clients must correctly follow the
[workflow behavior contract](docs/contract.md).  The toolkit provides an API
in different languages to make following the contract simple.

AWS Lambda functions handle the triggering of logic after updating the
activity state, but this can be handled directly in the client code instead.



# Why Not SWF?

The AWS Simple Workflow (SWF) requires having a server make a *long poll* HTTP
request to Amazon.  This means the framework does not handle impromptu launching
of ECS or other services well.

Additionally, it requires a dedicated server for monitoring and acting upon
the decision activities.
