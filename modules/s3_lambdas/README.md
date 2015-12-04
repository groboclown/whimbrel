# Whimbrel S3 Lambdas Module

The S3 Lambdas module allows for running the [workflow lambdas](../workflow_lambdas)
off of events triggered by writing files to S3 using the [Simple Lambda API](../../docs/contract.md).

These require having the ability to write files out to an S3 bucket.  Unlike
the [dynamodb lambdas](../dynamodb_lambdas), this is just a matter of writing
to a file if the S3 bucket is mapped to a Docker directory, so the overhead
of the docker image requirements is much lighter.
