
exports = function() {
    var AWS = require('./AWS.js');
    var Q = require('q');

    // Values we can pass from the dynamodbConfig object into the
    // AWS constructor.
    var DYNAMODB_CONFIG_KEYS = [
        "accessKeyId",
        "secretAccessKey",
        "sessionToken",
        "credentials",
        "credentialProvider",
        "maxRetries",
        "maxRedirects",
        "httpOptions",
        "endpoint",
        "sslEnabled",
        "region"
    ];

    // ===========================================================
    // DbConnection class
    // A nice layer between the JS objects and the DynamoDB stuff.
    // This translates the callbacks into Q promises.
    // It also provides helper methods for common data usages
    // in the DynamoDB storage.

    /**
     *
     * dynamodbConfig: object w/ these values:
     *    "db_prefix": (string)
     *    "region": (string) (optional)
     */
    var DbConnection = function(dynamodbConfig) {
        this.__dynamodbConfig = dynamodbConfig;
        if (typeof(this.__dynamodbConfig.db_prefix) == 'undefined') {
            this.__dynamodbConfig.db_prefix = "whimbrel_";
        }
        this.__dynamodb = null;
    };


    /**
     * Calls out to the getItem API, and sends data.Item to the onLoadCallback function, or
     * the error (possibly an internal exception) to the onErrorCallback function.
     *
     * http://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/DynamoDB.html#getItem-property
     */
    DbConnection.prototype.read = function(getItemParams) {
        var deferred = Q.defer();
        try {
            this.__dynamoDb_getConnection().getItem(getItemParams, function(err, data) {
                if (err) {
                    deferred.reject(err);
                } else {
                    deferred.resolve(data.Item);
                }
            });
        } catch (e) {
            deferred.reject(e);
        }
        return deferred.promise;
    };

    /**
     * A layer on top of the dynamodb API for query, where we expect there
     * to be exactly one entry with a primary key, even if the table defines
     * a range index.  If the query returns 0 or more than 1 result, then
     * the promise is resolved with a null value, otherwise, it is resolved
     * with the Item record with the requested key.
     */
    DbConnection.prototype.readByKey = function(tableName,
            primaryKeyName, primaryKeyType, primaryKeyValue) {
        var params = {
            TableName: tableName,
            Select: 'ALL_ATTRIBUTES',
            Limit: 2,
            KeyConditionExpression: primaryKeyName + ' = :hashKey',
            ExpressionAttributeValues: {
                hashKey: { primaryKeyType: primaryKeyValue }
            }
        };
        var deferred = Q.defer();
        try {
            this.__dynamoDb_getConnection().query(params, function(err, data) {
                if (err) {
                    deferred.reject(err);
                } else {
                    if (! data.Items || data.Items.length != 1) {
                        deferred.resolve(null);
                    } else {
                        deferred.resolve(data.Items[0]);
                    }
                }
            });
        } catch (e) {
            deferred.reject(e);
        }
        return deferred.promise;
    };

    DbConnection.prototype.update = function(saveItemParams) {
        var deferred = Q.defer();
        try {
            this.__dynamoDb_getConnection().updateItem(saveItemParams, function(err, data) {
                if (err) {
                    deferred.reject(err);
                } else {
                    deferred.resolve(data);
                }
            });
        } catch (e) {
            deferred.reject(e);
        }
        return deferred.promise;
    };

    DbConnection.prototype.create = function(saveItemParams) {
        var deferred = Q.defer();
        try {
            this.__dynamoDb_getConnection().putItem(saveItemParams, function(err, data) {
                if (err) {
                    deferred.reject(err);
                } else {
                    deferred.resolve(data);
                }
            });
        } catch (e) {
            deferred.reject(e);
        }
        return deferred.promise;
    };

    DbConnection.prototype.getTableName = function(name) {
        return this.__dynamodbConfig.db_prefix + name;
    };

    /**
     * Returns a tuple (epoch time, [year, month (Jan = 1), day (1 = 1), 24-hour, minute, second])
     * in UTC.
     */
    DbConnection.prototype.mkTime = function() {
        var d = new Date();
        return [
            d.UTC(),
            [ d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), d.getUTCHours(), d.getUTCMinutes(), d.getUTCSeconds() ]
        ];
    };

    DbConnection.prototype.mkItemTimeList = function(timeArray) {
        return [
            {"N": timeArray[0]},
            {"N": timeArray[1]},
            {"N": timeArray[2]},
            {"N": timeArray[3]},
            {"N": timeArray[4]},
            {"N": timeArray[5]}
        ];
    };

    DbConnection.prototype.mkUuid = function() {
        // See http://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
        var d = new Date().getTime();
        if(window.performance && typeof window.performance.now === "function"){
            d += performance.now(); //use high-precision timer if available
        }
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = (d + Math.random()*16)%16 | 0;
            d = Math.floor(d/16);
            return (c=='x' ? r : (r&0x3|0x8)).toString(16);
        });
        return uuid;
    };

    DbConnection.prototype.__dynamoDb_getConnection = function() {
        if (this.__dynamodb !== null) {
            var dynConfig = {};
            for (var i = 0; i < DYNAMODB_CONFIG_KEYS.length; i++) {
                if (typeof(this.__dynamodbConfig[DYNAMODB_CONFIG_KEYS[i]]) !== 'undefined') {
                    dynConfig[DYNAMODB_CONFIG_KEYS[i]] = this.__dynamodbConfig[DYNAMODB_CONFIG_KEYS[i]];
                }
            }
            this.__dynamodb = new AWS.DynamoDB(dynConfig);
        }
        return this.__dynamodb;
    };

    return DbConnection;
}();
