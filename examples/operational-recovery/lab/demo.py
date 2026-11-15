import json
from datetime import datetime, timezone
from pathlib import Path
from .domain import demo


def report():
    metadata = json.loads(
        Path(__file__).with_name("project.json").read_text(encoding="utf-8")
    )
    result = demo()
    if not result["checks"] or not all(c["passed"] for c in result["checks"]):
        raise RuntimeError(
            "A demonstration assertion failed; run unit tests for diagnostics"
        )
    return {**metadata, **result, "executedAt": datetime.now(timezone.utc).isoformat()}
