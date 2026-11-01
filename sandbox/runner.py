"""Runs inside an isolated disposable container, never on the host."""
import json
from pathlib import Path
import subprocess
import sys

payload = json.load(sys.stdin)
Path("/work/solution.py").write_text(payload["code"], encoding="utf-8")
Path("/work/test_solution.py").write_text(payload["tests"], encoding="utf-8")
raise SystemExit(subprocess.call([
    sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short", "/work/test_solution.py"
]))
