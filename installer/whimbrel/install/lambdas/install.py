
from ..cfg import Config
from .bundle import bundle_lambdas

def install_lambdas(config):
    assert isinstance(config, Config)
    bundled_lambda_zips = {}
    for module_name in config.modules:
        module = config.load_modules()[module_name]
        # Every module has a get_lambdas() function
        bundled_lambda_zips.update(bundle_lambdas(config, module.get_lambdas()))
    # FIXME conditionally upload the lambdas.


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
