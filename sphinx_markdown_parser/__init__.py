"""Write markdown inside docutils & Sphinx projects."""

from __future__ import annotations

from sphinx.application import Sphinx

from sphinx_markdown_parser.parser import MarkdownParser

__version__ = "0.3.0"


def setup(app: Sphinx) -> dict[str, object]:
    """Register the markdown parser as a Sphinx extension.

    Adding ``"sphinx_markdown_parser"`` to ``extensions`` in ``conf.py``
    registers ``MarkdownParser`` for ``.md`` sources along with the
    ``markdown_parser_config`` config value. Projects that need the
    ``CommonMarkParser`` or custom source suffixes can skip the extension and
    register a parser manually in their own ``setup(app)`` instead.
    """
    app.add_source_suffix(".md", "markdown", override=True)
    app.add_source_parser(MarkdownParser, override=True)
    app.add_config_value("markdown_parser_config", {}, "env")
    return {"version": __version__, "parallel_read_safe": True}
