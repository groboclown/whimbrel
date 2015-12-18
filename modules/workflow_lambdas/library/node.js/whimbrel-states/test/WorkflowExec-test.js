
var whimbrel_states = require('whimbrel-states');
var sinon = require('sinon');

function mkDbConnection() {
    return {
        read: sinon.stub(),
        readByKey: sinon.stub(),
        update: sinon.stub(),
        create: sinon.stub(),
        mkTime: function() {},
        mkItemTimeList: function(timeArray) {},
        mkUuid: function() {}
    };
};


describe('WorkflowExec', function() {

    describe("")

});
