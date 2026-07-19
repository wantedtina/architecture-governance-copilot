"""Routed Human Review page."""

from pathlib import Path
from runpy import run_path

_APP_NAMESPACE = run_path(
    str(Path(__file__).resolve().parents[1] / "app.py"),
    run_name="architecture_governance_copilot_page",
)
_APP_NAMESPACE["_render_review_page"]()
