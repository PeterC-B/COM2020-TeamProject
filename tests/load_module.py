import importlib.util
import pathlib
import sys

def load_module(path: str, name: str = None):
    """
    Load a Python module directly from a file path, bypassing package imports.
    This avoids executing server.app.__init__ and keeps AWS imports untouched.
    """
    file_path = pathlib.Path(path).resolve()
    module_name = name or file_path.stem

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)

    # Register module so imports inside it work normally
    sys.modules[module_name] = module

    spec.loader.exec_module(module)
    return module
