"""Sphinx configuration for the sphinx-markdown-parser documentation."""

from __future__ import annotations

from sphinx_markdown_parser import __version__
from sphinx_markdown_parser.parser import CommonMarkParser
from sphinx_markdown_parser.transform import AutoStructify

project = "Sphinx Markdown Parser"
author = "Clay Risser"
copyright = "2019, Clay Risser"
version = __version__
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
]

exclude_patterns = ["_build"]
html_theme = "alabaster"


def setup(app):
    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(CommonMarkParser)
    app.add_config_value(
        "markdown_parser_config",
        {
            "auto_toc_tree_section": "Contents",
            "enable_eval_rst": True,
        },
        "env",
    )
    app.add_transform(AutoStructify)
