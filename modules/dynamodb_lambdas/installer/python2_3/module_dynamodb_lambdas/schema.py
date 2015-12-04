"""
Describes the workflow_lambdas module database tables.
"""

from whimbrel.install.db import DbTableDef

DYNAMODB_LAMBDAS_DB_TABLES = {
    "workflow_request": DbTableDef(
        version=1,
        pk=["workflow_request_id", "S", "workflow_name", "S"],
        indexes={},
        attributes={
            "source": "S",
            "manual": "B",
            "when_epoch": "N"
        },
        extra_columns={
            "when": "L[I,I,I,I,I,I]"
        },
        stream=True
    ),
    "activity_event": DbTableDef(
        version=1,
        pk=["activity_event_id", "S", "activity_exec_id", "S"],
        indexes={},
        attributes={
            "source": "S",
            "manual": "B",
            "transition": "S"
        },
        extra_columns={
            "when": "L[I,I,I,I,I,I]"
        },
        stream=True
    ),
    "workflow_lambda": DbTableDef(
        version=1,
        pk=["workflow_name", "S"],
        indexes={},
        attributes={
            "lambda": "S"
        },
        extra_columns={},
        stream=False
    )
}
