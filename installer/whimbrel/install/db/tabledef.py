"""
Definition type for the DynamoDB tables.
"""


class DbTableDef(object):
    # Note that the definition does not know about the name.
    # This is to reduce cut-n-paste errors.
    def __init__(self, pk, indexes, attributes, stream, version):
        object.__init__(self)
        assert len(pk) == 2 or len(pk) == 4
        self.__s_pk = pk
        self.__s_indexes = indexes
        self.__s_attributes = attributes
        self.__s_stream = stream
        self.__attributes = None
        self.__indexes = None
        self.__version = version

    @property
    def version(self):
        return self.__version

    @property
    def key_schema(self):
        pk = [{'AttributeName': self.__s_pk[0], 'KeyType': 'HASH'}]
        if len(self.__s_pk) == 4:
            pk.append({'AttributeName': self.__s_pk[2], 'KeyType': 'RANGE'})
        return pk

    @property
    def stream_specification(self):
        if self.__s_stream:
            return {'StreamEnabled': True, 'StreamViewType': 'NEW_IMAGE'}
        return {'StreamEnabled': False}

    @property
    def attributes(self):
        if self.__attributes is None:
            self.__attributes, self.__indexes = self._create_attributes_and_local_indexes()
        return self.__attributes

    @property
    def local_indexes(self):
        if self.__indexes is None:
            self.__attributes, self.__indexes = self._create_attributes_and_local_indexes()
        return self.__indexes

    @property
    def throughput(self):
        # TODO figure out how to tweak the throughput parameters.
        # http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithTables.html#ProvisionedThroughput
        return {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 6}

    def _create_attributes_and_local_indexes(self):
        indexes = []
        attributes = [
            {
                "AttributeName": self.__s_pk[0],
                "AttributeType": self.__s_pk[1]
            }
        ]
        if len(self.__s_pk) == 4:
            attributes.append({"AttributeName": self.__s_pk[2], "AttributeType": self.__s_pk[3]})

        for (iname, itype) in self.__s_indexes.items():
            indexes.append({
                "IndexName": iname + "_index",
                "KeySchema": [{
                        "AttributeName": self.__s_pk[0],
                        "KeyType": 'HASH'
                    }, {
                        "AttributeName": iname,
                        "KeyType": 'RANGE'
                }],
                "Projection": {
                    "ProjectionType": "ALL"
                }
            })
            attributes.append({
                "AttributeName": iname,
                "AttributeType": itype
            })

        # Attributes are only for the key schema
        # for (aname, atype) in self.__s_attributes.items():
        #     attributes.append({
        #         "AttributeName": aname,
        #         "AttributeType": atype
        #     })

        return attributes, indexes
