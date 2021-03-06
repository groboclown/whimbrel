"""
Configuration object
"""

from boto3.session import Session
import types
import os
import sys
import importlib

# Note that these are ordered.
SUPPORTED_MODULES = (
    # The base module is "core", which everyone gets.
    "core",

    # Lambda Triggers lookup workflow execution decision logic
    # through DynamoDB, and call the corresponding lambda function.
    "workflow_lambdas",

    # Triggers lambda logic using simple API S3 events.
    # Requires the "workflow_lambdas".
    "s3_simple_client_api",

    # Triggers lambda logic using simple API DynamoDB events.
    # Requires the "workflow_lambdas".
    "dynamodb_simple_client_api"
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
    config = Config(categories)

    # Validation
    if "workflow_lambdas" not in config.modules:
        assert "s3_simple_client_api" not in config.modules
        assert "module_core" not in config.modules

    return config


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

        "default iam role": None,
        "iam roles": {
            "on_db_activity_event": None,
            "on_db_workflow_request": None
        }
    },
    'setup': {
        'db prefix': 'whimbrel_',
    },
    'modules': ['core'],
    'nodejs': {
        "npm exec": 'npm',
        "node exec": 'node'
    },
    'overrides': {
        'lambda dir': None,
        'cache dir': None
    }
}


class Config(object):
    def __init__(self, categories=None):
        object.__init__(self)
        self.__loaded_modules = None
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
        self.basedir = 'basedir' in self.__params and self.__params['basedir'] or os.path.dirname(sys.argv[0])

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
    def _nodejs(self):
        return self.get_category('nodejs')

    @property
    def _overrides(self):
        return self.get_category('overrides')

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
    def cache_dir(self):
        return self._overrides['cache dir'] or os.path.join(self.basedir, ".cache.d")

    @property
    def npm_exec(self):
        return self._nodejs['npm exec']

    @property
    def node_exec(self):
        return self._nodejs['node exec']

    @property
    def override_lambda_dir(self):
        return self._overrides['lambda dir'] or os.path.join(self.basedir, "user-overrides")

    @property
    def modules(self):
        """
        List of module names to installer.

        :return:
        """
        # 'core' module is always present, and is always first.
        modules = ['core']
        if 'modules' in self.__params:
            # look at SUPPORTED_MODULES first, to ensure we get the ordering right.
            for module in SUPPORTED_MODULES:
                if module not in modules and module in self.__params['modules']:
                    modules.append(module)
        return modules

    @property
    def module_paths(self):
        base_module_dir = os.path.join(os.path.dirname(sys.argv[0]), '..', 'modules')
        ret = {}
        for module_name in self.modules:
            ret[module_name] = os.path.join(base_module_dir, module_name)
        return ret


    def load_modules(self):
        if self.__loaded_modules is None:
            self.__loaded_modules = {}
            for module_name, module_path in self.module_paths:
                module_install_dir = os.path.join(module_path, 'installer')
                if module_install_dir not in sys.path:
                    sys.path.append(module_install_dir)
                self.__loaded_modules[module_name] = importlib.import_module('module_{0}'.format(module_name))
        return dict(self.__loaded_modules)

    def create_boto3_session(self):
        args = {}

        def pop(k):
            args[k] = self._aws[k]

        pop('aws_access_key_id')
        pop('aws_secret_access_key')
        pop('region_name')
        pop('aws_session_token')
        pop('profile_name')

        session = Session(**args)
        return session
