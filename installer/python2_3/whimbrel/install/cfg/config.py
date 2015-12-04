"""
Configuration object
"""

from boto3.session import Session
import types
import os

SUPPORTED_MODULES = (
    # The base module is "core", which everyone gets.
    "core",

    # Triggers lambda logic using S3 events.
    "s3_lambdas",

    # Triggers lambda logic using DynamoDB events.
    "dynamodb_lambdas",

    # Lambda Triggers lookup workflow execution decision logic
    # through DynamoDB, and call the corresponding lambda function.
    "workflow_lambdas"
)


def read_config(filename):
    # FIXME read from a file.  It should be a Python file.

    with open(filename, "r") as f:
        text = f.read() + "\n"
    config_compiled = compile(text, filename, "exec", dont_inherit=True)
    config_module = types.ModuleType(os.path.basename(filename), os.path.basename(filename))
    categories = {}
    exec(config_compiled, config_module.__dict__)
    for name in config_compiled.co_names:
        categories[name] = getattr(config_module, name)
    return Config(categories)


DEFAULTS = {
    "aws": {
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'region_name': None,
        'aws_session_token': None,
        'profile_name': None,
        'endpoint': None,
        'use ssl': True
    },
    'dynamodb': {
        'wait seconds': 5,
        'endpoint': None,
        'use ssl': None
    },
    "lambda": {
        'use ssl': None,
        'endpoint': None,
        "default iam role": None,
        "iam roles": {
            "on_db_activity_event": None,
            "on_db_workflow_request": None
        }
    },
    'setup': {
        'db prefix': 'whimbrel_',
    },
    'modules': ['core']
}


class Config(object):
    def __init__(self, categories=None):
        object.__init__(self)
        self.__params = categories or {}
        for key, value_dict in DEFAULTS.items():
            if key not in self.__params:
                if isinstance(value_dict, dict):
                    self.__params[key] = dict(value_dict)
                else:
                    self.__params[key] = list(value_dict)
            elif isinstance(value_dict, dict):
                for key2, val in value_dict.items():
                    if key2 not in self.__params[key]:
                        self.__params[key][key2] = val

    def get_category(self, name):
        if name not in self.__params:
            self.__params[name] = {}
        return self.__params[name]

    @property
    def _aws(self):
        return self.get_category('aws')

    @property
    def _dynamodb(self):
        return self.get_category('dynamodb')

    @property
    def _setup(self):
        return self.get_category('setup')

    @property
    def _lambda(self):
        return self.get_category('lambda')

    @property
    def db_prefix(self):
        return self._setup['db prefix']

    def set_db_prefix(self, db_prefix):
        assert isinstance(db_prefix, str)
        self._setup['db prefix'] = db_prefix

    @property
    def db_endpoint(self):
        return self._dynamodb['endpoint'] or self._aws['endpoint']

    def set_db_endpoint(self, db_endpoint):
        assert isinstance(db_endpoint, str)
        self._dynamodb['endpoint'] = db_endpoint

    @property
    def db_use_ssl(self):
        return self._dynamodb['use ssl'] is not None and self._dynamodb['use ssl'] or self._aws['use ssl']

    @property
    def db_wait_seconds(self):
        return self._dynamodb['wait seconds']

    def set_db_wait_seconds(self, val):
        assert isinstance(val, float) or isinstance(val, int)
        self._dynamodb['wait seconds'] = val

    @property
    def lambda_use_ssl(self):
        return self._lambda('use ssl') is not None and self._lambda['use ssl'] or self._aws['use ssl']

    @property
    def lambda_endpoint(self):
        return self._lambda['endpoint'] or self._aws['endpoint']

    @property
    def modules(self):
        """
        List of module names to install.

        :return:
        """
        modules = ["core"]
        if 'modules' in self.__params:
            for module in self.__params['modules']:
                if module not in modules and module in SUPPORTED_MODULES:
                    modules.append(module)
        return modules

    def create_boto3_session(self):
        args = dict(self._aws)

        session = Session(**args)
        return session
