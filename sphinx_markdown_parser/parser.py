"""Parser entry points for the docutils markdown parsers."""

from __future__ import annotations

from sphinx_markdown_parser.commonmark_parser import CommonMarkParser
from sphinx_markdown_parser.markdown_parser import MarkdownParser

__all__ = ["CommonMarkParser", "MarkdownParser"]
