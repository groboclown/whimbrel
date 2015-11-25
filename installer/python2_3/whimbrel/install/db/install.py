"""
Handles the schema creation and upgrade.
"""

import time
from ..cfg.config import Config
from ..util import out
from .tabledef import DbTableDef
from .schema_metadata import METADATA_DB_TABLES
from .schema_core import CORE_DB_TABLES
from .schema_workflow_lambdas import WORKFLOW_LAMBDAS_DB_TABLES

_TIMEOUT = [2]

MODULE_SCHEMA_MAP = {
    "core": CORE_DB_TABLES,
    "workflow_lambdas": WORKFLOW_LAMBDAS_DB_TABLES
}


def install_db(config):
    """
    Install or upgrade the DynamoDB tables.

    :param config:
    :return: None
    """
    assert isinstance(config, Config)
    _TIMEOUT[0] = config.db_wait_seconds
    client = _connect(config)
    db_prefix = config.db_prefix
    existing_tables = _load_tables(client, db_prefix)

    # These must be installed first; they should never be upgraded.
    for name, desc in METADATA_DB_TABLES.items():
        if name not in existing_tables:
            _create_table(client, db_prefix, name, desc)

    requested_tables = {}
    for module in config.modules:
        if module in MODULE_SCHEMA_MAP:
            requested_tables.update(MODULE_SCHEMA_MAP[module])
    remaining = _update_existing_tables(client, db_prefix, existing_tables, requested_tables)

    for (name, desc) in remaining.items():
        _create_table(client, db_prefix, name, desc)


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


def _update_existing_tables(client, db_prefix, existing_tables, requested_tables):
    """
    Updates the existing DynamoDB tables to have the expected schema.
    Returns the DB_TABLES table entries for the tables that do not
    exist.

    :param client:
    :param db_prefix: prefix for the db tables.
    :param existing_tables: result of a _load_tables call
    :return:
    """
    tables_not_existing = dict(requested_tables)

    for (name, desc) in existing_tables.items():
        if name in tables_not_existing:
            expected = tables_not_existing[name]
            del tables_not_existing[name]

            # TODO reference the install_status table to see
            # how to upgrade.

            _update_table(client, db_prefix, name, expected, desc)
        elif name not in METADATA_DB_TABLES:
            print("Unexpected existing table: {0}".format(name))

    return tables_not_existing


def _update_table(client, db_prefix, table_name, expected_state, current_state):
    """
    Updates an existing table to have the correct schema.

    :param client:
    :param table_name:
    :param expected_state:
    :param current_state:
    :return:
    """
    assert isinstance(expected_state, DbTableDef)
    name = db_prefix + table_name

    current_state = _wait_for_active(client, name, current_state)
    if 'Table' in current_state:
        current_state = current_state['Table']
    if 'TableDescription' in current_state:
        current_state = current_state['TableDescription']

    # print("current state: " + repr(current_state))

    desired_primary_key = expected_state.key_schema
    actual_primary_key = current_state['KeySchema']
    if desired_primary_key != actual_primary_key:
        # FIXME perform upgrade
        out.action("Upgrade", "Updating primary key")
        out.status("FAIL")
        raise NotImplementedError()

    desired_attributes = expected_state.attributes
    actual_attributes = current_state['AttributeDefinitions']
    if desired_attributes != actual_attributes:
        # FIXME perform upgrade
        out.action("Upgrade", "Updating attributes")
        out.status("FAIL")
        raise NotImplementedError()

    desired_index_desc = expected_state.local_indexes
    if len(desired_index_desc) > 0:
        if 'LocalSecondaryIndexes' in current_state and len(current_state['LocalSecondaryIndexes']) > 0:
            actual_index_desc = _strip_index_values(current_state['LocalSecondaryIndexes'])

            # indexes are a list, but order doesn't matter.  So, convert them into a
            # dictionary.
            ui_desired = {}
            for i in desired_index_desc:
                ui_desired[i['IndexName']] = i
            ui_actual = {}
            for i in actual_index_desc:
                ui_actual[i['IndexName']] = i

            if ui_desired != ui_actual:
                # FIXME perform upgrade
                out.action("Upgrade", "Updating secondary local indexes")
                out.status("FAIL")
                print("Expected indexes: " + repr(desired_index_desc))
                print("Actual indexes: " + repr(actual_index_desc))
                raise NotImplementedError()
        else:
            # FIXME perform upgrade
            out.action("Upgrade", "Updating secondary local indexes (adding them in)")
            out.status("FAIL")
            raise NotImplementedError()
    elif 'LocalSecondaryIndexes' in current_state and len(current_state['LocalSecondaryIndexes']) > 0:
            # FIXME perform upgrade
            out.action("Upgrade", "Updating secondary local indexes (removing them)")
            out.status("FAIL")
            raise NotImplementedError()

    # Don't do anything with GlobalSecondaryIndexes

    desired_stream_def = expected_state.stream_specification
    if desired_stream_def['StreamEnabled']:
        if 'StreamSpecification' not in current_state or not current_state['StreamSpecification']['StreamEnabled']:
            # FIXME perform upgrade
            out.action("Upgrade", "Updating stream (turn it on)")
            out.status("FAIL")
            raise NotImplementedError()
        elif current_state['StreamSpecification'] != desired_stream_def:
            # FIXME perform upgrade
            out.action("Upgrade", "Updating stream (change it)")
            out.status("FAIL")
            raise NotImplementedError()
    else:
        if 'StreamSpecification' in current_state and current_state['StreamSpecification']['StreamEnabled']:
            # FIXME perform upgrade
            out.action("Upgrade", "Updating stream (turn it off)")
            out.status("FAIL")
            raise NotImplementedError()

    # Don't mess with the provisioned throughput - assume the user can
    # adjust these as needed for the environment.

    # Change the install status of the object.
    client.put_item(
        TableName=db_prefix + 'install_status',
        Item={
            "object_id": {'S': 'table.' + name},
            "object_type": {'S': 'table'},
            "version": {'N': str(expected_state.version)},
            "description": {'S': "table"}
        }
    )


def _create_table(client, db_prefix, table_name, desc):
    """
    Create the table described.

    :param client:
    :param table_name: full name of the table-
    :param desc: DB_TABLES description
    """
    assert isinstance(db_prefix, str)
    assert isinstance(table_name, str)
    assert isinstance(desc, DbTableDef)
    name = db_prefix + table_name

    out.action("MkTable", "Creating table " + name)

    attribs = {
        "TableName": name,
        "KeySchema": desc.key_schema,
        "StreamSpecification": desc.stream_specification,
        "ProvisionedThroughput": desc.throughput
    }
    if len(desc.attributes) > 0:
        attribs["AttributeDefinitions"] = desc.attributes
    if len(desc.local_indexes) > 0:
        attribs["LocalSecondaryIndexes"] = desc.local_indexes

    # print("create table attributes: " + repr(attribs))
    response = client.create_table(**attribs)

    if response is None or not isinstance(response, dict) or 'TableDescription' not in response:
        # TODO make this a real type
        raise Exception("invalid response")

    _wait_for_active(client, name)

    client.put_item(
        TableName=db_prefix + 'install_status',
        Item={
            "object_id": {'S': 'table.' + table_name},
            "object_type": {'S': 'table'},
            "version": {'N': str(desc.version)},
            "description": {'S': "table"}
        }
    )


def _wait_for_active(client, name, last_read_table_def=None):
    """
    Wait until the table with the given name is 'ACTIVE'.

    :param client:
    :param name:
    :return:
    """

    waited = False
    while True:
        if last_read_table_def is None:
            out.waiting()
            last_read_table_def = client.describe_table(TableName=name)

        if _is_active(last_read_table_def):
            if waited:
                out.completed()
            return last_read_table_def

        if not waited:
            out.action("Waiting", "Waiting for table " + name + " to become active")
            waited = True

        time.sleep(_TIMEOUT[0])

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


def _strip_index_values(values):
    ret = []
    for index_def in values:
        stripped = {}
        if 'Projection' in index_def:
            stripped['Projection'] = {}
            for key, val in index_def['Projection'].items():
                # FIXME this can fail if complex projections are implemented
                stripped['Projection'][key.encode("ascii")] = val.encode("ascii")
        if 'KeySchema' in index_def:
            key_schema = []
            stripped['KeySchema'] = key_schema
            for ks in index_def['KeySchema']:
                ksh = {
                    'KeyType': ks['KeyType'].encode("ascii"),
                    'AttributeName': ks['AttributeName'].encode("ascii")
                }
                key_schema.append(ksh)
        if 'IndexName' in index_def:
            stripped['IndexName'] = index_def['IndexName'].encode("ascii")
        # ignore all other types
        ret.append(stripped)
    return ret


def _connect(config):
    """
    Creates a dynamodb low-level API client
    :param config:
    :return:
    """
    opt_args = {}
    if config.db_endpoint is not None:
        opt_args['endpoint_url'] = config.db_endpoint
    if config.db_use_ssl is not None:
        opt_args['use_ssl'] = config.db_use_ssl
    db = config.create_boto3_session().client('dynamodb', **opt_args)
    return db

