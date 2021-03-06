
// Overwrites the production version of "AWS.js"
exports = function() {
    var AWS = require('aws-sdk');

    // Overload the AWS configuration for testing purposes.
    AWS.config.loadFromPath("./test-aws-config.json");

    return AWS;
}();
