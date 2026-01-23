import json
from pathlib import Path

# Read version from package.json (single source of truth)
_pkg_json = Path(__file__).parent.parent.parent / "package.json"
__version__ = json.loads(_pkg_json.read_text())["version"]
