#!/bin/sh

# ENV requirements:
#   AWS_ACCESS_KEY=aws access key
#   AWS_SECRET_KEY=aws secret key
#   AWS_REGION=aws region for the request
# Arguments:
#   Arg 1: database prefix
#   Arg 2: DynamoDB endpoint URL (includes http:// or https://, but not trailing slash)
#   Arg 3: Host to connect to (in url)
#   Arg 4: Activity Exec ID
#   Arg 5: Transition (used to change the activity to a new state)
#   Arg 6: Source

here=`dirname $0`
if [ ! -f "${here}/core_aws_request.sh" ]; then
    echo "Not setup right."
    exit 1
fi

# Post an event to the dynamodb table.

dbPrefix="$1"
url="$2"
host="$3"
activity_exec_id="$4"
transition="$5"
source="$6"

# UUID
# This is Linux specific.
# FreeBSD should use /compat/linux/proc/sys/kernel/random/uuid
UUID=`cat /proc/sys/kernel/random/uuid`
activity_event_id="${activity_exec_id}::${UUID}"

date_epoch=`date -u +%s`
date_list=`date --date="@$date_epoch" +"[{\"N\":\"%Y\"},{\"N\":\"%-m\"},{\"N\":\"%-d\"},{\"N\":\"%-H\"},{\"N\":\"%-M\"},{\"N\":\"%-S\"}]"`

method=POST
targetPrefix=DynamoDB_20120810
target=${targetPrefix}.PutItem
jsonVersion=1.0
header="X-Amz-Target"
contentType="application/x-amz-json-${jsonVersion}"
payload_file=/tmp/$$.payload
echo '{"TableName":"'"${dbPrefix}"'activity_event","Item":{'\
    '"activity_event_id":{"S":"'"${activity_event_id}"'"},'\
    '"activity_exec_id":{"S":"'"${activity_exec_id}"'"},'\
    '"when_epoch":{"N":"'${date_epoch}'"},'\
    '"when":{"L":'${date_list}'},'\
    '"transition":{"S":"'"${transition}"'"},'\
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
