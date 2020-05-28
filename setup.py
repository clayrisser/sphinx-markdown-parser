from codecs import open
from os import path
from setuptools import setup, find_packages
import sphinx_markdown_parser

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = []
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires.extend(f.readlines())


setup(
    name='sphinx_markdown_parser',
    version=sphinx_markdown_parser.__version__,
    description=(
        'A docutils-compatibility bridge to markdown, '
        'enabling you to write markdown with support for tables '
        'inside of docutils & sphinx projects.'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/codejamninja/sphinx-markdown-parser',
    author='Jam Risser',
    author_email='jam@codejam.ninja',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='sphinx docs documentation markdown',
    packages=['sphinx_markdown_parser'],
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cm2html = sphinx_markdown_parser.scripts:cm2html',
            'cm2latex = sphinx_markdown_parser.scripts:cm2latex',
            'cm2man = sphinx_markdown_parser.scripts:cm2man',
            'cm2pseudoxml = sphinx_markdown_parser.scripts:cm2pseudoxml',
            'cm2xetex = sphinx_markdown_parser.scripts:cm2xetex',
            'cm2xml = sphinx_markdown_parser.scripts:cm2xml',
        ]
    }
)
