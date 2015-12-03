#!/bin/sh

# ENV requirements:
#   AWS_ACCESS_KEY=aws access key
#   AWS_SECRET_KEY=aws secret key
#   AWS_REGION=aws region for the request
# Arguments:
#   Arg 1: database prefix
#   Arg 2: DynamoDB endpoint URL (includes http:// or https://, but not trailing slash)
#   Arg 3: Host to connect to (in url)
#   Arg 4: workflow name
#   Arg 5: source

here=`dirname $0`
if [ ! -f "${here}/core_aws_request.sh" ]; then
    echo "Not setup right."
    exit 1
fi

# Post a request to the dynamodb table.

dbPrefix="$1"
url="$2"
host="$3"
workflow_name="$4"
source="$5"

# UUID
# This is Linux specific.
# FreeBSD should use /compat/linux/proc/sys/kernel/random/uuid
UUID=`cat /proc/sys/kernel/random/uuid`
workflow_request_id="${workflow_name}::${UUID}"

date_epoch=`date -u +%s`
date_list=`date --date="@$date_epoch" +"[{\"N\":\"%Y\"},{\"N\":\"%-m\"},{\"N\":\"%-d\"},{\"N\":\"%-H\"},{\"N\":\"%-M\"},{\"N\":\"%-S\"}]"`

method=POST
targetPrefix=DynamoDB_20120810
target=${targetPrefix}.PutItem
jsonVersion=1.0
header="X-Amz-Target"
contentType="application/x-amz-json-${jsonVersion}"
payload_file=/tmp/$$.payload
echo '{"TableName":"'"${dbPrefix}"'workflow_request","Item":{'\
    '"workflow_request_id":{"S":"'"${workflow_request_id}"'"},'\
    '"workflow_name":{"S":"'"${workflow_name}"'"},'\
    '"when_epoch":{"N":"'${date_epoch}'"},'\
    '"when":{"L":'${date_list}'},'\
    '"source":{"S":"'"${source}"'"}'\
    '}}' > ${payload_file}

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
