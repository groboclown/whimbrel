# Activity Execution Update through Simple Client API for `/bin/sh`

See [the sh / curl documents](../../../whimbrel-client-core/sh_curl) for details on the hows
and whys behind using a shell script for the simple client API.

## `request-workflow-exec.sh` usage

ENV requirements:

* `AWS_ACCESS_KEY` aws access key
* `AWS_SECRET_KEY` aws secret key
* `AWS_REGION` aws region for the request

Arguments:

* Arg 1: database prefix
* Arg 2: DynamoDB endpoint URL.  This includes `http://` or `https://`, but not the trailing slash.
    e.g. `http://localhost:8080`
* Arg 3: Host to connect to (in url)
* Arg 4: Activity Exec ID
* Arg 5: Transition (used to change the activity to a new state)
* Arg 6: Source
