
// Overwrites the production version of "AWS.js"
exports = function() {
    var AWS = {};

    // FIXME make a mock version.
    AWS.DynamoDB = function(config) {
        // do nothing
    };
    AWS.DynamoDB.prototype.getItem = function(params, callback) {

    };
    AWS.DynamoDB.prototype.putItem = function(params, callback) {

    };
    AWS.DynamoDB.prototype.updateItem = function(params, callback) {

    };
    AWS.DynamoDB.prototype.deleteItem = function(params, callback) {

    };
    AWS.DynamoDB.prototype.query = function(params, callback) {

    };
    return AWS;
}();
