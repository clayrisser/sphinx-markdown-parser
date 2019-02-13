
# -*- coding: utf-8 -*-

from sphinx_markdown_parser.parser import CommonMarkParser

templates_path = ['_templates']
source_suffix = '.md'
source_parsers = { '.md': CommonMarkParser }
master_doc = 'index'
project = u'sphinxproj'
copyright = u'2015, rtfd'
author = u'rtfd'
version = '0.1'
release = '0.1'
language = None
exclude_patterns = ['_build']
highlight_language = 'python'
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'sphinxproj'
