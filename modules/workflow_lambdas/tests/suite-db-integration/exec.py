

def setup(config):
    pass


def teardown(config):
    pass


def run_test(config):
    pass


def execute(config):
    setup(config)
    try:
        run_test(config)
    finally:
        teardown(config)
