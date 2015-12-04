
console.log("Loading on_workflow_request function");

var setup = require('whimbrel-setup');
var AWS = require('aws-sdk');
var dynamo = new AWS.DynamoDB.DocumentClass();

exports.handler = function(event, context) {
    // event methods:
    //  
};
