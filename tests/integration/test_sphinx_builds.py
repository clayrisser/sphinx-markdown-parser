"""Integration tests: build the Sphinx fixture projects and check the HTML."""

from __future__ import annotations

from pathlib import Path

import pytest
from sphinx.application import Sphinx

fixtures_dir = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def build(tmp_path_factory):
    outdirs: dict[str, Path] = {}

    def _build(fixture: str, filename: str = "index.html") -> str:
        if fixture not in outdirs:
            srcdir = fixtures_dir / fixture
            tmp_path = tmp_path_factory.mktemp(fixture)
            outdir = tmp_path / "html"
            app = Sphinx(
                srcdir=str(srcdir),
                confdir=str(srcdir),
                outdir=str(outdir),
                doctreedir=str(tmp_path / "doctrees"),
                buildername="html",
            )
            app.build(force_all=True)
            outdirs[fixture] = outdir
        return (outdirs[fixture] / filename).read_text(encoding="utf-8")

    return _build


def test_headings(build):
    output = build("sphinx_generic")
    for level in range(1, 5):
        assert (
            "<h{0}>Heading {0}"
            '<a class="headerlink" href="#heading-{0}"'.format(level)
        ) in output


def test_links(build):
    output = build("sphinx_generic")
    assert (
        'This is a <a class="reference external" href="http://example.com">link</a>'
    ) in output
    assert (
        'This is a <a class="reference external" '
        'href="http://example.com/foobar">ref link</a>'
    ) in output
    assert (
        'This is a <a class="reference external" ' 'href="/example">relative link</a>'
    ) in output
    assert '<span class="doc">pending ref</span>' in output


def test_image(build):
    output = build("sphinx_generic")
    assert '<img alt="Example" src="image.png"' in output


def test_paragraph(build):
    output = build("sphinx_generic")
    assert "<p>Foo</p>" in output
    assert "<p>Bar</p>" in output


def test_lists(build):
    output = build("sphinx_generic")
    assert (
        '<ul class="simple">\n'
        "<li><p>Item A</p></li>\n"
        "<li><p>Item B</p></li>\n"
        "<li><p>Item C</p></li>\n"
        "</ul>"
    ) in output
    assert (
        '<ol class="simple">\n'
        "<li><p>Item 1</p></li>\n"
        "<li><p>Item 2</p></li>\n"
        "<li><p>Item 3</p></li>\n"
        "</ol>"
    ) in output


def test_code(build):
    output = build("sphinx_generic")
    assert '<div class="highlight' in output
    assert "#!/bin/sh" in output


def test_thematic_break(build):
    output = build("sphinx_generic")
    assert '<p>Foo</p>\n<hr class="docutils" />\n<p>Bar</p>' in output


def test_code_block(build):
    output = build("sphinx_code_block")
    assert '<div class="highlight">' in output


def test_indented_code(build):
    output = build("sphinx_indented_code")
    assert '<div class="highlight">' in output


def test_nested_header_block(build):
    output = build("sphinx_nested_header_block")
    assert "<h1>" in output


def test_custom_suffix_and_embedded_rst(build):
    output = build("sphinx_custom_md")
    # the eval_rst table is rendered as a real table
    assert "<table " in output
    assert '<th class="head"><p>abc</p></th>' in output
    assert '<th class="head"><p>data</p></th>' in output
    assert "</table>" in output
    # the eval_rst contents directive produces a local table of contents
    assert '<p class="topic-title">Contents</p>' in output
    assert '<a class="reference internal" href="#header" id="id1">Header</a>' in output
    assert (
        '<a class="reference internal" href="#header-2" id="id2">Header 2</a>'
    ) in output


def test_inline_math(build):
    output = build("sphinx_inline_math")
    assert ">\\( E = mc^2 \\)<" in output
    assert ">$$<" in output
    assert ">$<" in output


def test_cross_references(build):
    output = build("sphinx_xref")
    # [link](link) and [absolute link](/link) resolve to the built document
    assert (
        '<a class="reference internal" href="link.html">'
        '<span class="doc">link</span></a>'
    ) in output
    assert (
        '<a class="reference internal" href="link.html">'
        '<span class="doc">absolute link</span></a>'
    ) in output
    assert (
        '<a class="reference external" '
        'href="http://www.google.com">external link</a>'
    ) in output
    # the referenced page itself is built
    assert "<h1>" in build("sphinx_xref", "link.html")
