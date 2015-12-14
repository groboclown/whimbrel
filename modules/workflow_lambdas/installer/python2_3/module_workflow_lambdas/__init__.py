
from .schema import WORKFLOW_LAMBDAS_DB_TABLES
from .lambdas import WORKFLOW_LAMBDAS_DEFS


def get_schema():
    return WORKFLOW_LAMBDAS_DB_TABLES


def get_lambdas():
    return dict(WORKFLOW_LAMBDAS_DEFS)


def get_states_library():
    return {
        "product": {
            "copy-dirs": [
                {
                    "srcdir": ["..", "modules", "workflow_lambdas", "library", "node.js", "src", "node_modules"],
                    "destdir": ["node_modules"]
                }
            ],
            "user-overrides": {
                "AWS.js": ["node_modules", "whimbrel-states", "AWS.js"]
            },
            "tokenized": [
                {
                    "srcdir": ["..", "modules", "workflow_lambdas", "library", "node.js", "tokenized"],
                    "destdir": ["."]
                }
            ],
            "npm": [
                "q"
            ]
        },
        "unit-tests": {
            "exec": [],
            "copy-dirs": [
                {
                    "srcdir": ["..", "modules", "workflow_lambdas", "library", "node.js", "unit-test", "node_modules"],
                    "destdir": ["node_modules"]
                },
                {
                    "srcdir": ["..", "modules", "workflow_lambdas", "library", "node.js", "unit-test", "test"],
                    "destdir": ["test"]
                }
            ],
            "npm": [
                "mocha", "sinon", "assert"
            ]
        },
        "integration-tests": {
            "exec": [],
            "copy-dirs": [
                {
                    "srcdir": ["..", "modules", "workflow_lambdas", "library", "node.js", "integration-test", "node_modules"],
                    "destdir": ["node_modules"]
                }
            ],
            "npm": [
                "mocha", "sinon", "assert"
            ]
        }
    }
