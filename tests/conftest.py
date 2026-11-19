import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _package(name, path=None):
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__path__ = []
        sys.modules[name] = module
    if path is not None:
        module.__path__ = [str(path)]
    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        setattr(sys.modules[parent_name], child_name, module)


_package("ansible_collections")
_package("ansible_collections.oceanbase")
_package("ansible_collections.oceanbase.ocp", ROOT)
