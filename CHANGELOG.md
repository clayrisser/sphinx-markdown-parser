# Changelog

## 0.3.0 (2026-08-12)

Revive and modernize the project.

- Support current Sphinx (7.x/8.x), docutils (0.19+), Python-Markdown (3.4+),
  and Python 3.10+
- Register the package as a proper Sphinx extension:
  `extensions = ["sphinx_markdown_parser"]`
- Expose YAML frontmatter as document metadata instead of discarding it
- Fix inline math rendering on modern Sphinx (backticks no longer leak into
  formulas)
- Fix embedded reStructuredText (`eval_rst`, autodoc) on modern Sphinx by
  declaring rst settings on the parsers
- Convert packaging to a uv-managed `pyproject.toml`; replace
  yapf/prospector/tox with black/basedpyright/pytest
- Remove the unused pydash dependency and dead code
- Document the project's niche honestly relative to MyST

## 0.2.4 and earlier

See the git history. Releases up to 0.2.4 were published to PyPI from the
original repository.
