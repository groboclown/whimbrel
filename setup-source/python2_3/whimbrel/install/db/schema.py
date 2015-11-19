"""
Handles the schema creation and upgrade.
"""

import time
from ..cfg.config import Config
from ..util import out

TIMEOUT = [2]


def install(config):
    assert isinstance(config, Config)
    TIMEOUT[0] = config.wait_time
    client = _connect(config)
    db_prefix = config.db_prefix
    existing_tables = _load_tables(client, db_prefix)
    remaining = _update_existing_tables(client, db_prefix, existing_tables)
    for (name, desc) in remaining.items():
        _create_table(client, db_prefix + name, desc)


DB_TABLES = {
    "workflow_request": {
        "pk": ["workflow_request_id", "S"],
        "index": {
            "workflow_name": "S"
        },
        "attributes": {
            "source": "S",
            "manual": "B",
            "when_epoc": "N"
        },
        "extra_columns": {
            "when": "L[I,I,I,I,I,I]"
        },
        "stream": True
    },
    "activity_event": {
        "pk": ["activity_event_id", "S"],
        "index": {
            "activity_exec_id": "S",
            "activity_name": "S",
            "workflow_exec_id": "S",
            "workflow_name": "S"
        },
        "attributes": {
            "source": "S",
            "manual": "B",
            "transition": "S",
            "when_epoc": "N"
        },
        "extra_columns": {
            "when": "L[I,I,I,I,I,I]"
        },
        "stream": True
    },
    "workflow_exec": {
        "pk": ["workflow_exec_id", "S"],
        "index": {
            "workflow_request_id": "S",
            "workflow_name": "S",
            "state": "S",
            "start_time_epoch": "N"
        },
        "extra_columns": {
            "start_time": "L[I,I,I,I,I,I]"
        },
        "stream": False
    },
    "activity_exec": {
        "pk": ["activity_exec_id", "S"],
        "index": {
            "workflow_exec_id": "S",
            "workflow_name": "S",
            "activity_name": "S",
            "state": "S",
            "start_time_epoch": "N",
            "heartbeat_time_epoch": "N",
            "heartbeat_enabled": "B"
        },
        "attributes": {
            "queue_time_epoc": "N",
            "end_time_epoc": "N"
        },
        "extra_columns": {
            "queue_time": "L[I,I,I,I,I,I]",
            "start_time": "L[I,I,I,I,I,I]",
            "end_time": "L[I,I,I,I,I,I]"
        },
        "stream": False
    },
    "activity_exec_dependency": {
        "pk": ["activity_exec_dependency_id", "S"],
        "index": {
            "activity_exec_id": "S",
            "workflow_exec_id": "S",
            "dependent_activity_exec_id": "S"
        },
        "attributes": {},
        "extra_columns": {},
        "stream": False
    }
}


def _load_tables(client, db_prefix):
    """
    Discovers the tables in the DynamoDB that start with the given
    prefix.  It returns the detailed table information in a dictionary.
    See https://boto3.readthedocs.org/en/latest/reference/services/dynamodb.html#DynamoDB.Client.describe_table
    for details about the table description.

    We use the low-level API because it gives us more control over the
    precise calls made, so we can reduce the data and call count.

    :param client: dynamodb client
    :param db_prefix: database table prefix (string)
    :return: dictionary, mapping the table name (string) to the
        table description (dictionary).  Think of it as a union of all
        the describe_table calls for the matching tables.  However,
        all the table names have the prefix stripped off.
    """
    out.action("Load Tables", "Discovering existing tables")

    args = {}
    tables = []
    has_more = True
    while has_more:
        response = client.list_tables(**args)
        if 'LastEvaluatedTableName' in response:
            args['ExclusiveStartTableName '] = response['LastEvaluatedTableName']
        else:
            has_more = False

        for name in response['TableNames']:
            if name.startswith(db_prefix):
                tables.append(name)

    ret = {}
    for name in tables:
        response = client.describe_table(TableName=name)
        table = response['Table']
        ret[table['TableName'][len(db_prefix):]] = table

    out.status("OK")
    return ret


def _update_existing_tables(client, db_prefix, existing_tables):
    """
    Updates the existing DynamoDB tables to have the expected schema.
    Returns the DB_TABLES table entries for the tables that do not
    exist.

    :param client:
    :param db_prefix: prefix for the db tables.
    :param existing_tables: result of a _load_tables call
    :return:
    """
    tables_not_existing = dict(DB_TABLES)

    for (name, desc) in existing_tables.items():
        if name in tables_not_existing:
            expected = tables_not_existing[name]
            del tables_not_existing[name]
            _update_table(client, db_prefix + name, expected, desc)
        else:
            print("Unexpected existing table: %s".format(name))

    return tables_not_existing


def _update_table(client, table_name, expected_state, current_state):
    """
    Updates an existing table to have the correct schema.

    :param client:
    :param table_name:
    :param expected_state:
    :param current_state:
    :return:
    """
    assert isinstance(expected_state, dict)

    out.action(table_name, "Checking for upgrade")

    current_state = _wait_for_active(client, table_name, current_state)
    if 'Table' in current_state:
        current_state = current_state['Table']

    primary_key = current_state['TableDescription']['KeySchema']
    # FIXME check primary key

    index_desc = current_state['TableDescription']['LocalSecondaryIndexes']
    # FIXME check secondary local indexes

    # Don't do anything with GlobalSecondaryIndexes

    stream_def = current_state['TableDescription']['StreamSpecification']
    # FIXME check stream def

    out.completed()

    # FIXME perform upgrade if necessary

    raise NotImplementedError()


def _create_table(client, name, desc):
    """
    Create the table described.

    :param client:
    :param name: full name of the table
    :param desc: DB_TABLES description
    """
    out.action(name, "Creating table")

    indexes = []
    attributes = [
        {
            "AttributeName": desc['pk'][0],
            "AttributeType": desc['pk'][1]
        }
    ]

    for (iname, itype) in desc['index'].items():
        attribute_type = {
            {
                "AttributeName": iname,
                "KeyType": itype
            }
        }
        indexes.append({
            "IndexName": iname + "_index",
            "KeySchema": [attribute_type],
            "Projection": {
                "ProjectionType": "ALL"
            }
        })
        attributes.append(attribute_type)

    for (aname, atype) in desc['attributes'].items():
        attributes.append({
            "AttributeName": aname,
            "AttributeType": atype
        })

    response = client.create_table(
        TableName=name,
        AttributeDefinitions=attributes,
        KeySchema=[{'AttributeName': desc['pk'][0], 'KeyType': 'HASH'}],
        LocalSecondaryIndexes=indexes,
        StreamSpecification={'StreamEnabled': desc['stream'], 'StreamViewType': 'NEW_IMAGE'},
        # TODO figure out how to tweak the throughput parameters.
        # http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithTables.html#ProvisionedThroughput
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 6}
    )

    if response is None or not isinstance(response, dict) or 'TableDescription' not in response:
        # TODO make this a real type
        raise Exception("invalid response")

    _wait_for_active(client, name)


def _wait_for_active(client, name, last_read_table_def=None):
    """
    Wait until the table with the given name is 'ACTIVE'.

    :param client:
    :param name:
    :return:
    """

    while True:
        if last_read_table_def is None:
            out.waiting()
            last_read_table_def = client.describe_table(TableName=name)

        if _is_active(last_read_table_def):
            return last_read_table_def

        time.sleep(TIMEOUT[0])

        last_read_table_def = None


def _is_active(table_def):
    """
    Is the table in an active state?

    :param table_def:
    :return:
    """
    assert table_def is not None
    if isinstance(table_def, dict) and 'Table' in table_def:
        table_def = table_def['Table']

    assert isinstance(table_def, dict)
    assert 'TableName' in table_def and 'TableStatus' in table_def

    return table_def['TableStatus'] == 'ACTIVE'


def _connect(config):
    """
    Creates a dynamodb low-level API client
    :param config:
    :return:
    """
    db = config.create_boto3_session().client('dynamodb')
    return db

