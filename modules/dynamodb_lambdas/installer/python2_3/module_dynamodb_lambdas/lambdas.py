
DYNAMODB_LAMBDAS = {
    "onDbActivityEvent": {
        "product": {
            "copy-files": [
                {
                    "src": ["..", "modules", "dynamodb_lambdas", "lambdas", "node.js", "src", "onDbActivityEvent.js"],
                    "dest": ["node_modules", "onDbActivityEvent", "index.js"]
                }
            ],
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
            # TODO add in test dirs
            #"copy-dirs": [
            #    {
            #        "srcdir": ["..", "modules", "dynamodb_lambdas", "lambdas", "node.js", "unit-test", "node_modules"],
            #        "destdir": ["node_modules"]
            #    }
            #],
            "npm": ["mocha"]
        },
        "integration-tests": {
            "exec": [],
            # TODO add in test dirs
            #"copy-dirs": [
            #    {
            #        "srcdir": ["..", "modules", "dynamodb_lambdas", "lambdas", "node.js", "integration-test", "node_modules"],
            #        "destdir": ["node_modules"]
            #    }
            #],
            "npm": ["mocha"]
        }
    }
}
