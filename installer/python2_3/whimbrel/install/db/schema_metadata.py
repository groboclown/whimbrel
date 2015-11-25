"""
Describes the metadata database tables, which everything else requires.
"""

from .tabledef import DbTableDef

METADATA_DB_TABLES = {
    "install_status": DbTableDef(
        version=1,
        pk=["object_id", "S", "object_type", "S"],
        indexes={},
        attributes={
            "version": "N",
            "description": "B"
        },
        extra_columns={},
        stream=False
    )
}
