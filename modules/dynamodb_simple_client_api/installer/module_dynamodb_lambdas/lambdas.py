
from whimbrel.install.lambdas import library
from module_workflow_lambdas import get_states_library

DYNAMODB_LAMBDAS = {
    "whimbrel-dynamodb-onActivityEvent": library.join_libraries({
        "product": {
            "copy-files": [
                {
                    "src": ["..", "modules", "dynamodb_simple_client_api", "lambdas", "node.js", "src", "index.js"],
                    "dest": ["node_modules", "whimbrel-dynamodb-onActivityEvent", "index.js"]
                }
            ]
        },
        "unit-tests": {
            "exec": [],
            "copy-dirs": [
                {
                    "srcdir": ["..", "modules", "dynamodb_simple_client_api", "lambdas", "node.js", "unit-tests"],
                    "destdir": ["."]
                },
            ]
        },
        "integration-tests": {
            "exec": [],
            "copy-dirs": [
                {
                    "srcdir": ["..", "modules", "dynamodb_simple_client_api", "lambdas", "node.js", "integration-tests"],
                    "destdir": ["."]
                },
            ]
        }
    }, get_states_library())
}
