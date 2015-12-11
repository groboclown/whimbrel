
from .schema import WORKFLOW_LAMBDAS_DB_TABLES
from .lambdas import WORKFLOW_LAMBDAS_DEFS


def get_schema():
    return WORKFLOW_LAMBDAS_DB_TABLES


def get_lambdas():
    return dict(WORKFLOW_LAMBDAS_DEFS)