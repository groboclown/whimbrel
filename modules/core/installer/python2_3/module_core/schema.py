"""
Describes the core database tables.
"""

from whimbrel.install.db import DbTableDef

CORE_DB_TABLES = {
    "workflow_exec": DbTableDef(
        version=1,
        pk=["workflow_exec_id", "S", "workflow_name", "S"],
        indexes={
            "state": "S",
            "start_time_epoch": "N"
        },
        attributes={
            "workflow_request_id": "S",
            "start_time": "L[I,I,I,I,I,I]"
        },
        stream=False
    ),
    "activity_exec": DbTableDef(
        version=1,
        pk=["activity_exec_id", "S", "workflow_exec_id", "S"],
        indexes={
            "state": "S",
            "start_time_epoch": "N",
            "heartbeat_time_epoch": "N"
        },
        attributes={
            "activity_name": "S",
            "workflow_name": "S",
            "queue_time_epoch": "N",
            "end_time_epoch": "N",
            "heartbeat_enabled": "BOOL",
            "queue_time": "L[I,I,I,I,I,I]",
            "start_time": "L[I,I,I,I,I,I]",
            "end_time": "L[I,I,I,I,I,I]"
        },
        stream=False
    ),
    "activity_exec_dependency": DbTableDef(
        version=1,
        pk=["activity_exec_dependency_id", "S", "activity_exec_id", "S"],
        indexes={
            "workflow_exec_id": "S",
            "dependent_activity_exec_id": "S"
        },
        attributes={},
        stream=False
    )
}
