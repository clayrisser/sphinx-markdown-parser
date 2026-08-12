"""Sphinx test fixture configuration."""

from __future__ import annotations

from sphinx_markdown_parser.parser import CommonMarkParser

project = "sphinxproj"
exclude_patterns = ["_build"]
highlight_language = "python"
html_theme = "alabaster"


def setup(app):
    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(CommonMarkParser)
