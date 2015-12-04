"""
Describes the workflow_lambdas module database tables.
"""

from whimbrel.install.db import DbTableDef

WORKFLOW_LAMBDAS_DB_TABLES = {
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
