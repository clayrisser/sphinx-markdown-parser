#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: setup.py
Author: Jam Risser
Date: 2019-02-13
"""

from setuptools import setup
import sphinx_markdown_parser

setup(
    name='sphinx_markdown_parser',
    version=sphinx_markdown_parser.__version__,
    description=('A docutils-compatibility bridge to markdown, '
                 'enabling you to write markdown with support for tables '
                 'inside of docutils & sphinx projects.'),
    url='https://github.com/codejamninja/sphinx-markdown-parser',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'Markdown>=3.0.1',
        'PyYAML==3.13',
        'commonmark>=0.7.3',
        'docutils>=0.11',
        'pydash==4.7.4',
        'sphinx>=1.3.1',
    ],
    entry_points={'console_scripts': [
        'cm2html = sphinx_markdown_parser.scripts:cm2html',
        'cm2latex = sphinx_markdown_parser.scripts:cm2latex',
        'cm2man = sphinx_markdown_parser.scripts:cm2man',
        'cm2pseudoxml = sphinx_markdown_parser.scripts:cm2pseudoxml',
        'cm2xetex = sphinx_markdown_parser.scripts:cm2xetex',
        'cm2xml = sphinx_markdown_parser.scripts:cm2xml',
    ]},
    packages=['sphinx_markdown_parser']
)
