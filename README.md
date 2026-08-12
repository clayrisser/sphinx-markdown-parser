# sphinx-markdown-parser

![](assets/sphinx-markdown-parser.png)

Write markdown inside of [docutils](https://docutils.sourceforge.io) &
[Sphinx](https://www.sphinx-doc.org) projects.

This is a docutils-compatibility bridge to
[Python-Markdown](https://github.com/Python-Markdown/markdown) and
[commonmark.py](https://github.com/readthedocs/commonmark.py). It grew out of
[recommonmark](https://github.com/readthedocs/recommonmark) at a time when
recommonmark lacked features such as tables, and it keeps that lineage's
`AutoStructify` transform for embedding reStructuredText inside markdown.

## Should you use this or MyST?

For most new Sphinx projects you should use
[MyST](https://myst-parser.readthedocs.io) (`myst-parser`). It is the parser
the Sphinx ecosystem standardized on after recommonmark was deprecated:
CommonMark-based, actively maintained, and it exposes Sphinx roles and
directives natively in markdown.

This project fills a narrower niche. Reach for it when:

* **You want the Python-Markdown dialect**, not CommonMark — for example your
  content relies on
  [Python-Markdown extensions](https://python-markdown.github.io/extensions/)
  such as `extra`, `toc`, `wikilinks`, or `nl2br`, or on the
  [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
  ecosystem.
* **You are maintaining a recommonmark-era project** and want to keep the
  `AutoStructify` behaviors (`eval_rst` blocks, auto toc trees, `$...$` inline
  math) without rewriting your markdown.
* **You want the `md2html`, `md2latex`, ... CLI bridges** for rendering
  markdown through plain docutils.

## Parsers

| **Parser**         | **Underlying Library**                        |
| ------------------ | --------------------------------------------- |
| `MarkdownParser`   | https://github.com/Python-Markdown/markdown   |
| `CommonMarkParser` | https://github.com/readthedocs/commonmark.py  |

`MarkdownParser` is the recommended and officially supported parser:

* It has more features, such as tables and the Python-Markdown extension
  ecosystem.
* Its underlying library is actively maintained.

`CommonMarkParser` is kept for backwards compatibility, but its underlying
library (commonmark.py) is unmaintained. If you want CommonMark, use
[MyST](https://myst-parser.readthedocs.io) instead.

## Getting Started

Install the package:

```sh
uv add sphinx-markdown-parser
# or
pip install sphinx-markdown-parser
```

If using `MarkdownParser`, you may also want to install some extensions for it:

```sh
uv add pymdown-extensions
```

Then enable the extension in your Sphinx `conf.py`:

```python
extensions = [
    "sphinx_markdown_parser",
]

markdown_parser_config = {
    "extensions": [
        "extra",
        "nl2br",
        "sane_lists",
        "smarty",
        "toc",
        "wikilinks",
    ],
}
```

This registers `MarkdownParser` for `.md` sources. This allows you to write
both `.md` and `.rst` files inside of the same project.

### Manual setup

If you need the `CommonMarkParser`, a custom source suffix, or more control,
skip the extension and register a parser yourself (do not combine this with
the `extensions` entry above):

```python
# for MarkdownParser
from sphinx_markdown_parser.parser import MarkdownParser


def setup(app):
    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(MarkdownParser)
    app.add_config_value(
        "markdown_parser_config",
        {
            "auto_toc_tree_section": "Content",
            "enable_auto_toc_tree": True,
            "enable_eval_rst": True,
            "extensions": [
                "extra",
                "nl2br",
                "sane_lists",
                "smarty",
                "toc",
                "wikilinks",
                "pymdownx.arithmatex",
            ],
        },
        "env",
    )


# for CommonMarkParser (please see the note above!)
from sphinx_markdown_parser.parser import CommonMarkParser


def setup(app):
    app.add_source_suffix(".md", "markdown")
    app.add_source_parser(CommonMarkParser)
    app.add_config_value(
        "markdown_parser_config",
        {
            "auto_toc_tree_section": "Content",
            "enable_auto_toc_tree": True,
            "enable_eval_rst": True,
            "enable_inline_math": True,
            "enable_math": True,
        },
        "env",
    )
```

### Frontmatter

YAML frontmatter at the top of a markdown file is stripped from the rendered
output and exposed as document metadata (`env.metadata` in Sphinx). Sphinx
metadata fields work from markdown, for example:

```markdown
---
orphan: true
author: Ada Lovelace
---

# My Page
```

### Links

For all links in commonmark that aren't explicit URLs, they are treated as
cross references with the
[`:any:`](https://www.sphinx-doc.org/en/master/usage/referencing.html#role-any)
role. This allows referencing a lot of things including files, labels, and
even objects in the loaded domain. `MarkdownParser` additionally rewrites
relative links to `.md` files into links to the built `.html` pages.

### AutoStructify

AutoStructify makes it possible to write your documentation in Markdown, and
automatically convert this into rST at build time. See
[the AutoStructify documentation](docs/auto_structify.md) for more information
about configuration and usage.

To use the advanced markdown to rst transformations you must add
`AutoStructify` to your Sphinx `conf.py`:

```python
# At top on conf.py (with other import statements)
from sphinx_markdown_parser.transform import AutoStructify


# At the bottom of conf.py
def setup(app):
    app.add_config_value(
        "markdown_parser_config",
        {
            "auto_toc_tree_section": "Contents",
        },
        "env",
    )
    app.add_transform(AutoStructify)
```

AutoStructify comes with the following options:

* __enable_auto_toc_tree__: enable the Auto Toc Tree feature.
* __auto_toc_tree_section__: when set, Auto Toc Tree will only be enabled on
  sections that match the title.
* __enable_auto_doc_ref__: enable the Auto Doc Ref feature. **Deprecated**
* __enable_math__: enable the Math Formula feature.
* __enable_inline_math__: enable the Inline Math feature.
* __enable_eval_rst__: enable the evaluate embedded reStructuredText feature.
* __url_resolver__: a function that maps an existing relative position in the
  document to an http link

## CLI

The package installs docutils front ends for rendering markdown directly:
`md2html`, `md2latex`, `md2man`, `md2pseudoxml`, `md2xetex`, and `md2xml`.

```sh
md2html README.md > README.html
```

## Development

The project is managed with [uv](https://docs.astral.sh/uv) and a
conventions-aligned Makefile:

```sh
make prepare    # one-time toolchain setup (asdf install + uv sync)
make test       # unit + integration tests with coverage
make test/e2e   # build the sample Sphinx project end to end
make lint       # black --check + basedpyright
make format     # black
make build      # build sdist + wheel into dist/
make docs       # build the documentation
```

## Recommended Projects

* [sphinx-markdown-builder](https://github.com/clayrisser/sphinx-markdown-builder) -
  sphinx builder that outputs markdown files

## Why a bridge?

Many python tools (mostly for documentation creation) rely on `docutils`.
But [docutils][dc] only supports a ReStructuredText syntax.

For instance [this issue][sphinx-issue] and [this StackOverflow
question][so-question] show that there is an interest in allowing `docutils`
to use markdown as an alternative syntax.

## Acknowledgement

sphinx-markdown-parser is based on [recommonmark][rcm].

recommonmark is mainly derived from [remarkdown][rmd] by Steve Genoud and
leverages the python CommonMark implementation.

It was originally created by [Luca Barbato][lu-zero], and was maintained in
the Read the Docs (rtfd) GitHub organization.

[rcm]: https://github.com/readthedocs/recommonmark
[rmd]: https://github.com/sgenoud/remarkdown
[lu-zero]: https://github.com/lu-zero

[dc]: https://docutils.sourceforge.io/docs/ref/doctree.html
[sphinx-issue]: https://github.com/sphinx-doc/sphinx/issues/825
[so-question]: https://stackoverflow.com/questions/2471804/using-sphinx-with-markdown-instead-of-rst
