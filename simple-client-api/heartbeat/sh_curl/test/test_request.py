
# FIXME make an actual test function

import subprocess
import os
import sys
import re

CATS = None


def get_config():
    global CATS
    if CATS is None:
        if os.path.dirname(sys.argv[0]) not in sys.path:
            sys.path.append(os.path.dirname(sys.argv[0]))
        from setup_tests import load_config
        CATS = load_config()
        if 'db prefix' not in CATS['dynamodb']:
            CATS['dynamodb']['db prefix'] = 'whimbrel_'
    return CATS


def run_command(workflow_exec_id, activity_exec_id):
    config = get_config()
    endpoint = config['dynamodb']['endpoint']
    m = re.match(r'^\w+:\/\/([^:]+):.*$', endpoint)
    if not m:
        raise Exception("bad url: " + repr(endpoint))
    host = m.group(1)
    exec_file = os.path.join(os.path.dirname(sys.argv[0]), '..', 'src', 'heartbeat.sh')
    cmd = [exec_file, config['dynamodb']['db prefix'], endpoint, host, workflow_exec_id, activity_exec_id]
    env = dict(os.environ)
    env['AWS_ACCESS_KEY'] = config['aws']['aws_access_key_id']
    env['AWS_SECRET_KEY'] = config['aws']['aws_secret_access_key']
    env['AWS_REGION'] = config['aws']['region_name']

    print("Running " + repr(cmd))
    sp = subprocess.Popen(cmd, env=env)
    return sp.wait()


if __name__ == '__main__':
    workflow_exec_id = sys.argv[1]
    activity_exec_id = sys.argv[2]

    run_command(workflow_exec_id, activity_exec_id)
