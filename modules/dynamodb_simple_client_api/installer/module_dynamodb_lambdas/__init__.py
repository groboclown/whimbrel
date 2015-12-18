
from .schema import DYNAMODB_LAMBDAS_DB_TABLES
from .lambdas import DYNAMODB_LAMBDAS


def get_schema():
    return DYNAMODB_LAMBDAS_DB_TABLES


def get_lambdas():
    return dict(DYNAMODB_LAMBDAS)
