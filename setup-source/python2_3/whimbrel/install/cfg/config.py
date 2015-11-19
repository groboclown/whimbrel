"""
Configuration object
"""

from boto3.session import Session

class Config(object):
    def __init__(self):
        object.__init__(self)
        self.__params = {}

    def set_aws_region(self, region):
        assert isinstance(region, str)
        self.__params['region'] = region

    def set_aws_access_key_id(self, key):
        assert isinstance(key, str)
        self.__params['aws_access_key_id'] = key

    def set_aws_secret_access_key(self, key):
        assert isinstance(key, str)
        self.__params['aws_secret_access_key'] = key

    @property
    def db_prefix(self):
        return 'dbprefix' in self.__params and self.__params['dbprefix'] or 'whimbrel_'

    def set_db_prefix(self, db_prefix):
        assert isinstance(db_prefix, str)
        self.__params['db_prefix'] = db_prefix

    @property
    def db_local(self):
        return 'dblocal' in self.__params and self.__params['dblocal'] or False

    def create_boto3_session(self):
        args = {}

        def put_if(key1, key2=None):
            if key2 is None:
                key2 = key1
            if key1 in self.__params:
                args[key2] = self.__params[key1]
                
        put_if('aws_access_key_id')
        put_if('aws_secret_access_key')
        put_if('aws_secret_access_key')
        put_if('aws_region', 'region_name')
        put_if('aws_session_token')
        put_if('aws_profile_name', 'profile_name')

        session = Session(**args)
        return session
