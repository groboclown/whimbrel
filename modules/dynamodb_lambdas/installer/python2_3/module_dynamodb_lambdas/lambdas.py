
from whimbrel.install.lambdas import library
from module_workflow_lambdas import get_states_library

DYNAMODB_LAMBDAS = {
    "onDbActivityEvent": library.join_libraries({
        "product": {
            "copy-files": [
                {
                    "src": ["..", "modules", "dynamodb_lambdas", "lambdas", "node.js", "src", "onDbActivityEvent.js"],
                    "dest": ["node_modules", "onDbActivityEvent", "index.js"]
                }
            ]
        },
        "unit-tests": {
            "exec": [],
            "copy-dirs": [
                {
                    "srcdir": ["..", "modules", "dynamodb_lambdas", "lambdas", "node.js", "unit-tests"],
                    "destdir": ["."]
                },
            ]
        },
        "integration-tests": {
            "exec": [],
            "copy-dirs": [
                {
                    "srcdir": ["..", "modules", "dynamodb_lambdas", "lambdas", "node.js", "integration-tests"],
                    "destdir": ["."]
                },
            ]
        }
    }, get_states_library())
}
