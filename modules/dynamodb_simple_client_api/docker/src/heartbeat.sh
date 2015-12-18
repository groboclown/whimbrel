#!/bin/sh

# ENV requirements:
#   AWS_ACCESS_KEY=aws access key
#   AWS_SECRET_KEY=aws secret key
#   AWS_REGION=aws region for the request
# Arguments:
#   Arg 1: database prefix
#   Arg 2: DynamoDB endpoint URL (includes http:// or https://, but not trailing slash)
#   Arg 3: Host to connect to (in url)
#   Arg 4: Workflow Exec ID
#   Arg 5: Activity Exec ID

here=`dirname $0`
if [ ! -f "${here}/core_aws_request.sh" ]; then
    echo "Not setup right."
    exit 1
fi

# Post an event to the dynamodb table.

dbPrefix="$1"
url="$2"
host="$3"
workflow_exec_id="$4"
activity_exec_id="$5"

date_epoch=`date -u +%s`

method=POST
targetPrefix=DynamoDB_20120810
target=${targetPrefix}.UpdateItem
jsonVersion=1.0
header="X-Amz-Target"
contentType="application/x-amz-json-${jsonVersion}"
payload_file=/tmp/$$.payload
echo '{"TableName":"'"${dbPrefix}"'activity_exec",'\
    '"Key":{'\
    '"activity_exec_id":{"S":"'"${activity_exec_id}"'"},'\
    '"workflow_exec_id":{"S":"'"${workflow_exec_id}"'"}},'\
    '"UpdateExpression":"SET heartbeat_time_epoch=:epoch",'\
    '"ConditionExpression":"attribute_exists(heartbeat_enabled) AND heartbeat_enabled=:true",'\
    '"ExpressionAttributeValues":{":epoch":{"N":"'"${date_epoch}"'"},":true":{"BOOL": true}}'\
    '}' > ${payload_file}

# NOTE: Add -D for debug mode
exec ${here}/core_aws_request.sh \
    -s dynamodb \
    -r "${method}" \
    -p "/" \
    -f "${payload_file}" \
    -c "${contentType}" \
    -h "${host}" \
    -x "${url}" \
    -d "${header}" "${target}"
