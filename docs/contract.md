# Contract for Whimbrel Clients

As Whimbrel has no central server to ensure correct operations, each client must
follow the "contract" to ensure proper behavior.

There are two ways to fulfill the client contract.  The simple method relies upon
the execution of Lambdas, triggered by inserts into the DynamoDB.  If you would
prefer to execute the full logic in process (and not incur the cost of Lambda
invocations), the logic API must be used instead.  Note that each has its own
limitations.

The two major behaviors that client API must handle is initiating a workflow,
and marking a change in activity state.  The workflow initiation can be done
from any source, whereas the activity state change should only be handled from
the activities themselves.


## Simple Lambda API

### Initiate a New Workflow

The workflow execution begins by inserting a single item into the
`whimbrel_workflow_request` table.


### Update Activity State

When an activity runs, it must be aware of its *Activity Exec ID*, which
uniquely identifies the activity that's running.  This is usually an argument
passed to the process, but it can also be an evironment variable or contained
in a file in S3, or any other approach that's suitable to your environment.

There are two ways to go about updating the activity state, either by writing a
file to a well-defined S3 bucket, or by writing a single record to a DynamoDB
table.


### S3 File Activity State Update

For the S3 file version of the activity state update, the application must write
a file to a well-defined S3 location.  The file name must be `(activity exec id).state`
with contents equals to the current state.  When the file is created or updated,
the Lambda will pick up the change and fire the correct state processing.


### DynamoDB Table Activity State Update

For the Simple Lambda API, the API clients only need to send a single
write to the `whimbrel_activity_event` table, and the registered Lambda functions handle
the rest of the logic.

The Lambda that initiated a state activity should pass to the execution
environment the `activity_exec_id` so that the event table can be correctly populated.

The insert requires the specification of these attributes:


### Activity Heartbeat

*TODO finish*



## Full Logic API

The full logic API puts the activity and workflow execution flow into the
client process.  This applies for both the Lambda functions which
are triggered off up updates from the Simple Lambda API, and clients that
directly run this logic to avoid the Lambda cost or delays.

### Workflow Execution

A workflow execution has the following states:

* `REQUESTED` the workflow is initiated, awaiting the activities to be queued.
* `RUNNING` when the workflow has begin processing.  This happens as soon as
  an action begins to act upon the workflow.
* `FAILED_WAITING` if any of the activities finished in such a way that it triggers the
  workflow to fail, but activities are still running.
* `FAILED` if the workflow failed, an all the activities are stopped.
* `CANCEL_REQUESTED` when an external source requests the cancellation of the
  workflow.
* `CANCELLED` when the workflow was cancelled, and all the activities are stopped.
* `COMPLETED` when the activities have all stopped in a way that did not trigger a failure in the
    workflow.

#### Requesting a workflow

The `whimbrel_workflow_request` insert should be inserted, but with the
`manual` attribute set to True, to prevent the Lambda functions (if they
exist) from attempting to start the workflow on their own.  It's not
necessary to add to this table, but it is useful for tracing.  Note that
this table can only be added to if the dynamodb_lambdas module is installed.

The `whimbrel_workflow_exec` then needs to have a new item added.  The
initial state is `REQUESTED`.

#### Starting the Workflow

When a workflow execution begins, the state is updated to `RUNNING`, then
the transition decision for the workflow executes, which populates the
list of activities and their dependencies.  For the `whimbrel_lambdas`
module, the `run` attribute of the `whimbrel_workflow_lambda` table
is called, and that lambda must initialize the activities and their dependencies.

Each of the initial activities that run for the workflow are
added into the `whimbrel_activity_exec`, with an initial state of
`REQUESTED`, then the `whimbrel_activity_exec_dependency` table
is inserted to (if necessary).

Finally, the activities requested must be triggered.  See below.

(TODO: whimbrel_lambdas includes additional lambdas for state
transitions, and responding to activity failures.)


### Update Activity States and Transitions.

In order to have a decentralized system where each part isn't stepping
on another's toes, the state transitions are strictly defined, and all
Full Logic API users must obey them.

#### States

An activity enters these states:

* `REQUESTED` when the activity is noted on first insert into `whimbrel_activity_exec`.
* `READY` when the dependent activities have completed.
* `QUEUED` when the system has submitted the activity for execution, in order to
  prevent other parts of the system to do the same.
* `PREPARING` for when the environment to run the activity needs special setup.
  Very distinct from an actual activity that this activity depends upon (as that would
  be another environment).  Some activities may not need this, and go straight to
  `RUNNING` from `QUEUED`.
* `RUNNING` when the activity execution system starts, the state is set to `RUNNING`.
  At this point, the system must push heartbeats (if heartbeats are enabled) or
  it will be considered a broken activity.
* `CANCELLED` when an external source cancelled the activity, while the activity
  was not running.
* `CANCELLED_RUNNING` when an external source cancelled the activity, but the
  activity was still running.
* `TIMED_OUT` when the heartbeat was not received in time.
* `FAILED` when the activity completed with an unexpected error, preventing
  dependent activities from running.
* `COMPLETED` when the activity completed running without an error.

#### Activity Execution Transitions

* Current state `REQUESTED`:
  * `CANCEL` - turn the activity to `CANCELLED`.  Can happen if the
    user requests a cancellation, or if this activity depends on another
    one that failed.
  * `READY` - turn the activity to `READY`.   Should only happen when
    the last of its dependencies enters `COMPLETED` state.
  * `QUEUED` - turn the activity to `QUEUED`.  Should only happen when this
    is the first activity for the workflow and the activity has no
    dependencies.
* Current state `READY`:
  * `CANCEL` - turn the activity to `CANCELLED`.  Can happen if the
    user requests a cancellation, or if this activity depends on another
    one that failed.
  * `QUEUED` - turn the activity to `QUEUED`.  Happens when another
    thread or process on the same computer launches, or when the docker
    container is launched, or a task is requested to run in ECS, and
    so on. 
  * `PREPARING` - turn the activity to `PREPARING`.  Should only happen
    when the actor checking the activity immediately runs the activity,
    without needing to use a different process to perform the
    actual execution.
  * `RUNNING` - turn the activity to `RUNNING`.  Should only happen
    when the actor checking the activity immediately runs the activity,
    without going through an environment procurement phase.
* Current state `QUEUED`:
  * `CANCEL` - turn the activity to `CANCELLED`.
  * `PREPARING` - turn the activity to `PREPARING`.
  * `RUNNING` - turn the activity to `RUNNING`.
  * `FAILED` - turn the activity to `FAILED`.  Can happen if environment
    preparation cannot complete.
* Current state is `PREPARING`:
  * `CANCEL` - turn the activity to `CANCELLED`.
  * `RUNNING` - turn the activity to `RUNNING`.
  * `FAILED` - turn the activity to `FAILED`.  Can happen if environment
    preparation cannot complete.
* Current state is `RUNNING`:
  * `CANCEL` - turn the activity to `CANCELLED_RUNNING`.
  * `FAILED` - turn the activity to `FAILED`.
  * `COMPLETED` - turn the activity to `COMPLETED`.
* Current state is `CANCELLED_RUNNING`:
* Terminal statees (no transitions):
  * `CANCELLED`
  * `TIMED_OUT` - note that, in this state, the activity could potentially
    still be running, but the rest of the system has assumed that it has
    failed.  The running activity, if it notices this state, can update other
    aspects of the `whimbrel_activity_exec` table, but it must not change
    the state.
  * `FAILED`
  * `COMPLETED`



### Launching A New Activity

The actual mechanism to execute the activities is up to the client, and
not all requested activities need to be executed now.  Those that are
requested to run must have the `REQUESTED` state change to `QUEUED`.
This must be a conditional update; if the update fails, then it should
be assumed that the activity has been queued by another part of the
system.

### Original design

Quick notes on how the system should work, designed around docker.
      
#### Workflow is queued:

1. workflow table is inserted with initial data.

#### Activity is queued:

1. Activities are added to activity table.  Multiple are
   added only in the case of parallel jobs.  State is "pending".
1. All activities queued (up to a maximum limit) are launched
   as new docker images specific to that activity.  Those that
   are queued have their state set to "queued", all others to
   "pending" when the activity is inserted.  actual docker tasks
   are launched *after* the values are all inserted.

#### Activity is started (run in docker task):

1. Check the workflow entry to see if it's "running", and
   stops if it is something else.  Maybe set activity info as well.
1. Set activity state to "running" and set the start date.
1. Start a heartbeat thread to set the heartbeat date on the
   object.

#### Activity stops with error (run in docker task):

1. Caught failures set the workflow state and activity state.
   Could be done by the wrapping shell script that launched the
   process.

#### Activity stops successfully (run in docker task):

1. explicitly decrement the activity counter when the counter is
   set to the expected value.  If the value is 0, then that means
   there aren't additional activities in the current parallel
   runs, and the next activity steps can be run.
1. If the count is greater than 0, query for activities that are
   pending, and set the first activity state to "queued" if the
   value is "pending"; if that fails, then someone else picked
   that activity up, so move to the next activity in the list
   and try again.  If the update was successful, launch a new
   docker task to run that activity.

#### Heartbeat Listener:

1. Something that runs at a scheduled interval checks the workflow
   state.
1. For each failed or completed workflow, the activities
   that are pending will be changed to "never started" (or something).
1. For each "running" activity whose heartbeat is too long ago,
   mark it as "unresponsive" and fail the workflow.

