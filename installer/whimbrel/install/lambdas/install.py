
from ..cfg import Config


def install_lambdas(config):
    pass


def _connect_lambda(config):
    assert isinstance(config, Config)
    opt_args = {
        'api_version': '2015-03-31'
    }
    if config.db_endpoint is not None:
        opt_args['endpoint_url'] = config.lambda_endpoint
    if config.db_use_ssl is not None:
        opt_args['use_ssl'] = config.lambda_use_ssl
    session = config.create_boto3_session()
    return session.client('lambda', **opt_args)
