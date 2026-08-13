"""End-to-end test: build a real Sphinx project that uses MarkdownParser.

The sample project registers the parser through the
``sphinx_markdown_parser`` extension and exercises the markdown constructs
the parser supports: headings, inline markup, fenced code blocks, tables,
links, lists, blockquotes, and YAML frontmatter.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sphinx.application import Sphinx

sample_project = Path(__file__).parent / "sample_project"


@pytest.fixture(scope="module")
def build(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("sample_project")
    outdir = tmp_path / "html"
    app = Sphinx(
        srcdir=str(sample_project),
        confdir=str(sample_project),
        outdir=str(outdir),
        doctreedir=str(tmp_path / "doctrees"),
        buildername="html",
    )
    app.build(force_all=True)
    return app, outdir


def test_headings_become_sections_with_anchors(build):
    _, outdir = build
    index = (outdir / "index.html").read_text(encoding="utf-8")
    assert "<h1>Sample Project" in index
    assert "<h2>Usage" in index
    assert 'href="#usage"' in index
    assert 'href="#comparison"' in index


def test_inline_markup(build):
    _, outdir = build
    index = (outdir / "index.html").read_text(encoding="utf-8")
    assert "<strong>markdown</strong>" in index
    assert "<em>Sphinx</em>" in index
    assert '<span class="pre">sphinx-markdown-parser</span>' in index


def test_fenced_code_block_is_highlighted(build):
    _, outdir = build
    index = (outdir / "index.html").read_text(encoding="utf-8")
    # the ```py language tag survives into a pygments-highlighted block
    assert '<div class="highlight-py notranslate">' in index
    assert '<span class="k">def</span>' in index
    assert "hello" in index


def test_table(build):
    _, outdir = build
    index = (outdir / "index.html").read_text(encoding="utf-8")
    assert "<table" in index
    assert "</table>" in index
    assert "<p>tool</p>" in index
    assert "<p>packaging</p>" in index
    assert "<p>formatting</p>" in index


def test_links(build):
    _, outdir = build
    index = (outdir / "index.html").read_text(encoding="utf-8")
    # links to .md files are rewritten to the built .html pages
    assert 'href="page.html"' in index
    # external links are left alone
    assert 'href="https://www.sphinx-doc.org"' in index


def test_lists_and_blockquote(build):
    _, outdir = build
    index = (outdir / "index.html").read_text(encoding="utf-8")
    assert "<ul" in index
    assert "<ol" in index
    assert "<p>first</p>" in index
    assert "<p>one</p>" in index
    assert "<blockquote>" in index
    assert "Markdown inside Sphinx." in index


def test_frontmatter_becomes_metadata(build):
    app, outdir = build
    index = (outdir / "index.html").read_text(encoding="utf-8")
    # frontmatter must not leak into the rendered page ...
    assert "Ada Lovelace" not in index
    assert "category" not in index
    # ... it is exposed as document metadata instead
    assert app.env.metadata["index"]["author"] == "Ada Lovelace"
    assert app.env.metadata["index"]["category"] == "example"
    # page.md opted out of toctree warnings via `orphan: true`
    assert app.env.metadata["page"]["orphan"]


def test_linked_page_is_built(build):
    _, outdir = build
    page = (outdir / "page.html").read_text(encoding="utf-8")
    assert "<h1>Another Page" in page
