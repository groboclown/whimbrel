
exports = function() {
    var ret = {};

    var WorkflowExec = require('./WorkflowExec.js');
    var ActivityExec = require('./ActivityExec.js');

    ret.startWorkflow = function(workflowName) {
        // FIXME
    };

    ret.getWorkflowExec = function(workflowExecId, workflowName) {
        // FIXME
    };

    ret.createActivity = function(workflowExec, activityName, dependsOnList) {
        // FIXME
    };

    ret.getActivityExec = function(activityExecId, workflowExecId) {
        // FIXME
    };

    ret.getActivityDependencies = function(activityExecId, workflowExecId) {
        // FIXME
    };



    return ret;
}();


