#!/usr/bin/python

from boto3.session import Session
import sys
import os
import uuid
import time


def get_env(name):
    if name in os.environ:
        return os.environ[name]
    return None


aws_args = {
    'aws_access_key_id': get_env('AWS_ACCESS_KEY'),
    'aws_secret_access_key': get_env('AWS_SECRET_KEY'),
    'region_name': get_env('AWS_REGION'),
    'aws_session_token': get_env('AWS_SESSION_TOKEN'),
    'profile_name': get_env('AWS_PROFILE_NAME')
}
AWS_ARG_MAP = {
    '--ak': 'aws_access_key_id',
    '--as': 'aws_secret_access_key',
    '--ar': 'region_name',
    '--at': 'aws_session_token',
    '--ap': 'profile_name'
}
dynamodb_args = {}

db_prefix = 'whimbrel_'
workflow_name = None
activity_name = None
source = 'Python CLI'

i = 1
while i < len(sys.argv):
    # AWS specific setup
    if sys.argv[i] in AWS_ARG_MAP:
        arg = sys.argv[i]
        i += 1
        aws_args[AWS_ARG_MAP[arg]] = sys.argv[i]

    # DynamoDB specific setup
    elif sys.argv[i] == '--endpoint':
        i += 1
        dynamodb_args['endpoint_url'] = sys.argv[i]
    elif sys.argv[i] == '--ssl':
        dynamodb_args['use_ssl'] = True

    # Whimbrel specific setup
    elif sys.argv[i] == '--prefix':
        i += 1
        db_prefix = sys.argv[i]
    elif sys.argv[i] == '--workflow':
        i += 1
        workflow_name = sys.argv[i]
    elif sys.argv[i] == '--activity':
        i += 1
        activity_name = sys.argv[i]
    elif sys.argv[i] == '--source':
        i += 1
        source = sys.argv[i]
    i += 1

session = Session(**aws_args)
db = session.client('dynamodb', **dynamodb_args)

# ------------------------------------------------------------------
# Step 1: create the workflow exec entry

workflow_exec_id = workflow_name + '::' + str(uuid.uuid1())
print("Creating workflow_exec_id=" + workflow_exec_id)
when_epoch = int(time.time() - 1000)
when_gm = time.gmtime(when_epoch)
when_list = [
    {"N": str(when_gm.tm_year)},
    {"N": str(when_gm.tm_mon)},
    {"N": str(when_gm.tm_mday)},
    {"N": str(when_gm.tm_hour)},
    {"N": str(when_gm.tm_min)},
    {"N": str(when_gm.tm_sec)}
]


db.put_item(
    TableName=db_prefix + 'workflow_exec',
    Item={
        "workflow_exec_id": {"S": workflow_exec_id},
        # No workflow request ID, because this isn't originating from a request
        # "workflow_request_id": {"S": "-"},
        "state": {"S": "RUNNING"},
        "start_time": {"L": when_list},
        "start_time_epoch": {"N": str(when_epoch)},
        "workflow_name": {"S": workflow_name}
    }
)

# Step 2: create the activity exec entry

activity_exec_id = activity_name + '::' + str(uuid.uuid1())
print("Creating activity_exec_id="+activity_exec_id)
when_epoch = int(time.time() - 500)
when_gm = time.gmtime(when_epoch)
when_list = [
    {"N": str(when_gm.tm_year)},
    {"N": str(when_gm.tm_mon)},
    {"N": str(when_gm.tm_mday)},
    {"N": str(when_gm.tm_hour)},
    {"N": str(when_gm.tm_min)},
    {"N": str(when_gm.tm_sec)}
]


db.put_item(
    TableName=db_prefix + 'activity_exec',
    Item={
        "activity_exec_id": {"S": activity_exec_id},
        "workflow_exec_id": {"S": workflow_exec_id},
        "activity_name": {"S": activity_name},
        "workflow_name": {"S": workflow_name},
        "heartbeat_enabled": {"BOOL": True},
        "state": {"S": "RUNNING"},
        "start_time": {"L": when_list},
        "start_time_epoch": {"N": str(when_epoch)},
        "heartbeat_time_epoch": {"N": str(when_epoch)},
        "queued_time": {"L": when_list},
        "queued_time_epoch": {"N": str(when_epoch)},
        "source": {"S": source}
    }
)
