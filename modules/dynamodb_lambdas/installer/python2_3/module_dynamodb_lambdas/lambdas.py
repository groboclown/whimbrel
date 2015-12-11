
DYNAMODB_LAMBDAS = {
    "onDbActivityEvent": {
        "product": {
            "copy-files": [
                {
                    "src": ["dynamodb_lambdas", "lambdas", "node.js", "src", "onDbActivityEvent.js"],
                    "dest": ["node_modules", "onDbActivityEvent", "index.js"]
                }
            ],
            "copy-dirs": [
                {
                    "srcdir": ["workflow_lambdas", "library", "node.js", "src", "node_modules"],
                    "destdir": ["node_modules"]
                }
            ],
            "user-overrides": {
                "AWS.js": ["node_modules", "whimbrel-states", "AWS.js"]
            },
            "tokenized": [
                {
                    "srcdir": ["workflow_lambdas", "library", "node.js", "tokenized"],
                    "destdir": []
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
                    "srcdir": ["dynamodb_lambdas", "lambdas", "node.js", "unit-test", "node_modules"],
                    "destdir": ["node_modules"]
                }
            ],
            "npm": [ "mocha" ]
        },
        "integration-tests": {
            "exec": [],
            "copy-dirs": [
                {
                    "srcdir": ["dynamodb_lambdas", "lambdas", "node.js", "integration-test", "node_modules"],
                    "destdir": ["node_modules"]
                }
            ],
            "npm": [ "mocha" ]
        }
    }
}
