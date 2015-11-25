"""
Describes the core database tables.
"""

from .tabledef import DbTableDef

CORE_DB_TABLES = {
    "workflow_request": DbTableDef(
        version=1,
        pk=["workflow_request_id", "S", "workflow_name", "S"],
        indexes={},
        attributes={
            "source": "S",
            "manual": "B",
            "when_epoc": "N"
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
    "workflow_exec": DbTableDef(
        version=1,
        pk=["workflow_exec_id", "S", "workflow_request_id", "S"],
        indexes={
            "state": "S",
            "start_time_epoch": "N"
        },
        attributes={
            "workflow_name": "S"
        },
        extra_columns={
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
            "queue_time_epoc": "N",
            "end_time_epoc": "N",
            "heartbeat_enabled": "B"
        },
        extra_columns={
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
        extra_columns={},
        stream=False
    )
}
