#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI scripts for docutils CommonMark parser

Author: Steve Genoud
Date: 2013-08-25
Description: Scripts loaded by setuptools entry points
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except ImportError:
    pass

from docutils.core import publish_cmdline, default_description
from sphinx_markdown_parser.parser import MarkdownParser

def md2html():
    description = (
        'Generate html document from markdown sources. ' + default_description
    )
    publish_cmdline(
        writer_name='html', parser=MarkdownParser(), description=description
    )

def md2man():
    description = (
        'Generate a manpage from markdown sources. ' + default_description
    )
    publish_cmdline(
        writer_name='manpage',
        parser=MarkdownParser(),
        description=description
    )

def md2xml():
    description = (
        'Generate XML document from markdown sources. ' + default_description
    )
    publish_cmdline(
        writer_name='xml', parser=MarkdownParser(), description=description
    )

def md2pseudoxml():
    description = (
        'Generate pseudo-XML document from markdown sources. ' +
        default_description
    )
    publish_cmdline(
        writer_name='pseudoxml',
        parser=MarkdownParser(),
        description=description
    )

def md2latex():
    description = (
        'Generate latex document from markdown sources. ' + default_description
    )
    publish_cmdline(
        writer_name='latex',
        parser=MarkdownParser(),
        description=description
    )

def md2xetex():
    description = (
        'Generate xetex document from markdown sources. ' + default_description
    )
    publish_cmdline(
        writer_name='latex',
        parser=MarkdownParser(),
        description=description
    )
