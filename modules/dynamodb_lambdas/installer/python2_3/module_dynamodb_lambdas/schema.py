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
            "when_epoch": "N",
            "when": "L[N,N,N,N,N,N]",
            "workflow_version": "N"
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
            "transition": "S",
            "when": "L[N,N,N,N,N,N]"
        },
        stream=True
    )
}
