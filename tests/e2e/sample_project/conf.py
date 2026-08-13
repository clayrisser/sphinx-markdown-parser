"""Sphinx configuration for the end-to-end sample project."""

from __future__ import annotations

project = "sample"
extensions = ["sphinx_markdown_parser"]
markdown_parser_config = {
    "extensions": ["extra", "sane_lists", "toc"],
}
exclude_patterns = ["_build"]
html_theme = "alabaster"
