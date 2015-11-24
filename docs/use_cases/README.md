# Whimbrel Usage

Whimbrel Core focuses on one thing - managing the state of workflow processes.
It leaves the details of setting up the actual workflows to the client code.


## General Pattern

The software should construct *workflows*, which defines a task that must be
accomplished, along with failure conditions.  The workflow expresses itself
through *activities* and *decisions* that are linked together through the
distributed Whimbrel Core state.

The *activities* are the long running bits of code that perform the real
work of the workflow.  The *decisions* are stateless bits of code that
control the list of future activities, or the overall state of the workflow,
by sending messages to Whimbrel Core.


## Launching Activities and Decisions

Because Whimbrel only defines the storage of the workflow state, and how the
workflow may transition to other states, the user has many options in how
the system can be shaped.

If the system uses AWS Lambdas to handle the state transitions, then the
decision execution and activity launching must also be done from within
the lambdas.  An extension (`workflow_lambdas`) allows for the core
Whimbrel lambdas to call out to custom lambdas when an activity execution
changes state.


## Use Cases

* [AWS Data Pipeline](aws_data_pipeline.md)
* [Smart Docker Instances](smart_docker.md)
* [Simple API Clients and Decision Lambdas](decision_lambdas.md)
