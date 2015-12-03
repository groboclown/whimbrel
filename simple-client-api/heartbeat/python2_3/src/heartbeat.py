#!/usr/bin/python

from boto3.session import Session
import sys
import os
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
activity_exec_id = None
workflow_exec_id = None
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
    elif sys.argv[i] == '--aei':
        i += 1
        activity_exec_id = sys.argv[i]
    elif sys.argv[i] == '--wei':
        i += 1
        workflow_exec_id = sys.argv[i]
    i += 1

session = Session(**aws_args)
db = session.client('dynamodb', **dynamodb_args)

when_epoch = int(time.time())

db.update_item(
    TableName=db_prefix + 'activity_exec',
    Key={
        "activity_exec_id": {"S": activity_exec_id},
        "workflow_exec_id": {"S": workflow_exec_id}
    },
    UpdateExpression="SET heartbeat_time_epoch = :epoch",
    ConditionExpression="attribute_exists(heartbeat_enabled) AND heartbeat_enabled=:true",
    ExpressionAttributeValues={
        ":epoch": {"N": str(when_epoch)},
        ":true": {"BOOL": True}
    }
)
