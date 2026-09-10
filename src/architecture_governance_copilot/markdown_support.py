"""Safe composition helpers for generated human-readable Markdown."""

from __future__ import annotations


def escape_markdown_text(value: str) -> str:
    """Render one structured value literally without allowing Markdown structure injection."""
    flattened = " ".join(value.replace("\r\n", "\n").replace("\r", "\n").splitlines())
    escaped: list[str] = []
    for character in flattened:
        if character in "\\`*_{}[]<>#":
            escaped.append("\\")
        escaped.append(character)
    return "".join(escaped)
