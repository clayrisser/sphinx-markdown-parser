# -*- coding: utf-8 -*-

from sphinx_markdown_parser.parser import CommonMarkParser

templates_path = ['_templates']
master_doc = 'index'
project = u'sphinxproj'
copyright = u'2015, rtfd'
author = u'rtfd'
version = '0.1'
release = '0.1'
highlight_language = 'python'
language = None
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'sphinxproj'


def setup(app):
    app.add_source_suffix('.md', 'markdown')
    app.add_source_parser(CommonMarkParser)
