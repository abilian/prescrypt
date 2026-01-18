from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

# Try to set memory limit (512 MB) to prevent OOM - only works on Linux
try:
    import resource

    MAX_MEMORY = 512 * 1024 * 1024  # 512 MB
    resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY, MAX_MEMORY))
except Exception:
    pass  # RLIMIT_AS not supported on macOS, or other error

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from prescrypt.compiler import py2js

source_path = sys.argv[1]
try:
    source = Path(source_path).read_text()
    js_code = py2js(source)
    print(
        json.dumps(
            {"status": "success", "js_code": js_code, "error": "", "traceback": ""}
        )
    )
except MemoryError:
    print(
        json.dumps(
            {
                "status": "error",
                "js_code": "",
                "error": "MemoryError: compilation exhausted memory limit",
                "traceback": "",
            }
        )
    )
except Exception as e:
    print(
        json.dumps(
            {
                "status": "error",
                "js_code": "",
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        )
    )
