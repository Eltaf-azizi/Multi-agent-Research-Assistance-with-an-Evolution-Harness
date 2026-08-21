import json
from pathlib import Path
from typing import Any, Dict, Optional


def save_metrics(metrics: Dict[str, Any], path: Optional[str] = None) -> None:
    target = Path(path or "evaluation/metrics.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)


def load_metrics(path: Optional[str] = None) -> Dict[str, Any]:
    target = Path(path or "evaluation/metrics.json")
    if not target.exists():
        return {}
    with target.open("r", encoding="utf-8") as handle:
        return json.load(handle)
