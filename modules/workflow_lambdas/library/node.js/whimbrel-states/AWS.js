
exports = function() {
    var AWS = require('aws-sdk');

    // Custom code to configure AWS.

    // See
    // http://docs.aws.amazon.com/AWSJavaScriptSDK/guide/node-configuring.html
    // for details on setting up the AWS.config object.

    // If this is left blank, then AWS will default to the IAM role for the
    // Lambda or EC2 instance (depending on where this is run from).

    return AWS;
}();
