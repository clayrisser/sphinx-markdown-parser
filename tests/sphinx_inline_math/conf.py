# -*- coding: utf-8 -*-

from sphinx_markdown_parser.parser import CommonMarkParser
from sphinx_markdown_parser.transform import AutoStructify

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
    app.add_config_value('markdown_parser_config', {
        'enable_inline_math': True,
    }, True)
    app.add_transform(AutoStructify)
