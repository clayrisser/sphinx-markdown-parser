"""Sphinx test fixture configuration."""

from __future__ import annotations

from sphinx_markdown_parser.parser import CommonMarkParser
from sphinx_markdown_parser.transform import AutoStructify

project = "sphinxproj"
exclude_patterns = ["_build"]
highlight_language = "python"
html_theme = "alabaster"


def setup(app):
    app.add_source_suffix(".markdown", "markdown")
    app.add_source_parser(CommonMarkParser)
    app.add_config_value(
        "markdown_parser_config",
        {
            "enable_eval_rst": True,
            "commonmark_suffixes": [".markdown"],
        },
        "env",
    )
    app.add_transform(AutoStructify)
