
import types
import os


def load_config(filename='setup.config'):
    with open(filename, "r") as f:
        text = f.read() + "\n"
    config_compiled = compile(text, filename, "exec", dont_inherit=True)
    config_module = types.ModuleType(os.path.basename(filename), os.path.basename(filename))
    categories = {}
    exec(config_compiled, config_module.__dict__)
    for name in config_compiled.co_names:
        categories[name] = getattr(config_module, name)
    return categories
