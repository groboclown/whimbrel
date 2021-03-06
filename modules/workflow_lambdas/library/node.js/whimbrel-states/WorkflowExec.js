
exports = function() {
    ret = {
        // FIXME move into the dynamodb_lambdas
        /**
         * Returns the workflowRequestId as the data value in the "then" call.
         */
        createWorkflowRequest: function(dbConnection, workflowName) {
            var workflowRequestId = workflowName + '::' + dbConnection.mkUuid();
            var time = dbConnection.mkTime();
            return dbConnection.create(
                {
                    TableName: dbConnection.getTableName('workflow_request'),
                    Item: {
                        workflow_request_id: { S: workflowRequestId },
                        workflow_name: { S: workflowName },
                        when_epoch: { N: time[0] },
                        when: { L: dbConnection.mkItemTimeList(time[1]) },
                        source: { S: 'whimbrel_lambda' },
                        manual: { BOOL: true }
                    },

                    ConditionExpression: "attribute_not_exist(workflow_request_id)"
                }
            ).then(function (item) {
                return workflowRequestId;
            });
        },


        /**
         * Returns a Q promise for the creation of the WorkflowExec object.
         */
        createWorkflowExec: function(dbConnection, workflowName, workflowRequestId) {
            var workflowExec = new WorkflowExec(dbConnection,
                workflowName + "::" + dbConnection.mkUuid(),
                workflowName,
                workflowRequestId);

            // Initial write
            return dbConnection.create(
                {
                    TableName: workflowExec.__tableName,
                    Item: {
                        workflow_exec_id: { S: workflowExec.getWorkflowExecId() },
                        workflow_name: { S: workflowExec.getWorkflowName() },
                        start_time: { L: dbConnection.mkItemTimeList(workflowExec.getStartTime()) },
                        start_time_epoch: { N: workflowExec.getStartTimeEpoch() },
                        state: { S: workflowExec.getState() },
                        workflow_request_id: { S: workflowExec.getWorkflowRequestId() }
                    },

                    // ensure that this is a brand new item, and not replacing an existing one.
                    ConditionExpression: "attribute_not_exists(workflow_exec_id)"
                }
            ).then(function (item) {
                return workflowExec;
            });
        },

        /**
         * Returns a Q promise for the reading of the WorkflowExec object.
         */
        readWorkflowExec: function(dbConnection, workflowExecId, workflowName) {
            var workflowExec = new WorkflowExec(dbConnection, workflowExecId, workflowName, null);

            return dbConnection.read({
                TableName: this._tableName("workflow_exec"),
                Key: {
                    "workflow_exec_id": { "S": workflowExec.getWorkflowExecId() },
                    "workflow_name": { "S": workflowExec.getWorkflowName() }
                }
            }).then(function (item) {
                workflowExec._updateFromLoad(item);

                return workflowExec;
            });
        }
    };



    // ===========================================================
    // WorkflowExec class
    var WorkflowExec = function(dbConnection, workflowExecId, workflowName, workflowRequestId) {
        this.__dbConnection = dbConnection;
        this.__tableName = dbConnection.getTableName('workflow_exec');

        this.__workflowExecId = workflowExecId;
        this.__workflowName = workflowName;
        this.__state = 'REQUESTED';
        var dateList = dbConnection.mkTime();
        this.__startTimeEpoch = dateList[0];
        this.__startTime = dateList[1];
        this.__workflowRequestId = workflowRequestId;
        return this;
    };




    WorkflowExec.prototype.getWorkflowExecId = function() {
        return this.__workflowExecId;
    };

    WorkflowExec.prototype.getWorkflowName = function() {
        return this.__workflowName;
    };

    WorkflowExec.prototype.getState = function() {
        return this.__state;
    };

    WorkflowExec.prototype.getStartTime = function() {
        return this.__startTime;
    };

    WorkflowExec.prototype.getStartTimeEpoch = function() {
        return this.__startTimeEpoch;
    };

    WorkflowExec.prototype.getWorkflowRequestId = function() {
        return this.__workflowRequestId;
    };


    /**
     * Transition the workflow to another state.
     */
    WorkflowExec.prototype.setState = function(stateName) {
        var we = this;
        stateName = stateName.toUpperCase();
        var oldState = this.getState();

        return this.__dbConnection.update({
            TableName: we.__tableName,
            Key: {
                workflow_exec_id: {"S": we.getWorkflowExecId()},
                workflow_name: {"S": we.getWorkflowName()}
            },
            UpdateExpression: "SET state = :newState",
            ConditionExpression: "state=:oldState",
            ExpressionAttributeValues: {
                ":newState": {"S": stateName},
                ":oldState": {"S": oldState}
            }
        }).then(function (data) {
            we.__state = stateName;
        });
    };

    WorkflowExec.prototype._updateFromLoad = function(item) {
        if (item.workflow_exec_id !== this.__workflowExecId ||
                item.workflow_name !== this.__workflowName) {
            // FIXME better error management
            throw new Exception("invalid return data");
        }

        this.__state = item.state;
        this.__startTimeEpoch = item.start_time_epoch;
        this.__startTime = item.start_time;
        this.__workflowRequestId = item.workflow_request_id;
    };

    return ret;
}();
