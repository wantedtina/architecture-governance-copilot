"""Contract tests for the deliberate light-only Streamlit theme."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
THEME_CONFIG_PATH = REPOSITORY_ROOT / ".streamlit" / "config.toml"


def load_theme_config() -> dict[str, object]:
    """Load the project-level Streamlit configuration as TOML."""
    return tomllib.loads(THEME_CONFIG_PATH.read_text(encoding="utf-8"))


def test_theme_is_one_explicit_light_only_configuration() -> None:
    config = load_theme_config()

    assert set(config) == {"theme"}
    theme = config["theme"]
    assert isinstance(theme, dict)
    assert theme["base"] == "light"
    assert "light" not in theme
    assert "dark" not in theme


def test_theme_uses_approved_main_and_sidebar_tokens() -> None:
    theme = load_theme_config()["theme"]
    assert isinstance(theme, dict)

    assert {
        "primaryColor": theme["primaryColor"],
        "backgroundColor": theme["backgroundColor"],
        "secondaryBackgroundColor": theme["secondaryBackgroundColor"],
        "textColor": theme["textColor"],
        "linkColor": theme["linkColor"],
        "codeBackgroundColor": theme["codeBackgroundColor"],
        "borderColor": theme["borderColor"],
        "redColor": theme["redColor"],
        "greenColor": theme["greenColor"],
        "blueColor": theme["blueColor"],
    } == {
        "primaryColor": "#D93636",
        "backgroundColor": "#F7F8FA",
        "secondaryBackgroundColor": "#EEF0F2",
        "textColor": "#061D33",
        "linkColor": "#0B56A8",
        "codeBackgroundColor": "#EEF0F2",
        "borderColor": "#D5DBE1",
        "redColor": "#D93636",
        "greenColor": "#238500",
        "blueColor": "#0B56A8",
    }
    assert theme["showWidgetBorder"] is True
    assert theme["showSidebarBorder"] is True

    sidebar = theme["sidebar"]
    assert isinstance(sidebar, dict)
    assert sidebar == {
        "primaryColor": "#238500",
        "backgroundColor": "#061D33",
        "secondaryBackgroundColor": "#0B2A47",
        "textColor": "#FFFFFF",
        "linkColor": "#B9D9FF",
        "codeTextColor": "#FFFFFF",
        "codeBackgroundColor": "#0B2A47",
        "borderColor": "#164365",
    }
