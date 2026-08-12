"""AST-level tests for CommonMarkParser."""

from __future__ import annotations

from textwrap import dedent

from docutils.utils import new_document

from sphinx_markdown_parser.parser import CommonMarkParser


def assert_parses(source, expected):
    parser = CommonMarkParser()
    parser.parse(dedent(source), new_document("<string>"))
    actual = dedent(parser.document.asdom().toprettyxml(indent="  "))
    assert actual == dedent(expected).lstrip()


def test_empty():
    assert_parses(
        """
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;"/>
        """,
    )


def test_heading():
    assert_parses(
        """
        # Heading 1

        ## Heading 2

        Body
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <section ids="heading-1" names="heading\\ 1">
            <title>Heading 1</title>
            <section ids="heading-2" names="heading\\ 2">
              <title>Heading 2</title>
              <paragraph>Body</paragraph>
            </section>
          </section>
        </document>
        """,
    )


def test_heading_inline():
    assert_parses(
        """# Heading *foo*""",
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <section ids="heading-foo" names="heading\\ foo">
            <title>
              Heading \n\
              <emphasis>foo</emphasis>
            </title>
          </section>
        </document>
        """,
    )


def test_paragraph():
    assert_parses(
        """This is a paragraph""",
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>This is a paragraph</paragraph>
        </document>
        """,
    )
    assert_parses(
        """This is a paragraph *foo***bar**""",
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            This is a paragraph \n\
            <emphasis>foo</emphasis>
            <strong>bar</strong>
          </paragraph>
        </document>
        """,
    )
    assert_parses(
        """
        This is a paragraph
        This is a new line
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            This is a paragraph


            This is a new line
          </paragraph>
        </document>
        """,
    )


def test_entities():
    assert_parses(
        """
        &copy;
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>©</paragraph>
        </document>
        """,
    )


def test_links():
    assert_parses(
        """
        This is a [link](http://example.com)
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            This is a \n\
            <reference refuri="http://example.com">link</reference>
          </paragraph>
        </document>
        """,
    )
    assert_parses(
        """
        This is a [link][example]

        [example]: http://example.com "Example"
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            This is a \n\
            <reference refuri="http://example.com" title="Example">link</reference>
          </paragraph>
        </document>
        """,
    )
    assert_parses(
        """
        This is a [link][example]

        [example]: http://example.com
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            This is a \n\
            <reference refuri="http://example.com">link</reference>
          </paragraph>
        </document>
        """,
    )
    assert_parses(
        """
        <http://example.com>
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            <reference refuri="http://example.com">http://example.com</reference>
          </paragraph>
        </document>
        """,
    )
    assert_parses(
        """
        [link](/foo)
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            <pending_xref refdomain="None" refexplicit="True" reftarget="/foo" reftype="any" refwarn="True">
              <reference refuri="/foo">link</reference>
            </pending_xref>
          </paragraph>
        </document>
        """,
    )
    assert_parses(
        """
        [link](foo)
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            <pending_xref refdomain="None" refexplicit="True" reftarget="foo" reftype="any" refwarn="True">
              <reference refuri="foo">link</reference>
            </pending_xref>
          </paragraph>
        </document>
        """,
    )
    assert_parses(
        """
        **[link](foo)**
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            <strong>
              <pending_xref refdomain="None" refexplicit="True" reftarget="foo" reftype="any" refwarn="True">
                <reference refuri="foo">link</reference>
              </pending_xref>
            </strong>
          </paragraph>
        </document>
        """,
    )


def test_image():
    assert_parses(
        """
        ![foo](/url "title")
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            <image alt="title" uri="/url">foo</image>
          </paragraph>
        </document>
        """,
    )


def test_inline_code():
    assert_parses(
        """
        This is `code` right?
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>
            This is \n\
            <literal>code</literal>
             right?
          </paragraph>
        </document>
        """,
    )


def test_bullet_list():
    assert_parses(
        """
        * List item 1
        * List item 2
        * List item 3
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <bullet_list>
            <list_item>
              <paragraph>List item 1</paragraph>
            </list_item>
            <list_item>
              <paragraph>List item 2</paragraph>
            </list_item>
            <list_item>
              <paragraph>List item 3</paragraph>
            </list_item>
          </bullet_list>
        </document>
        """,
    )
    assert_parses(
        """
        * [List item 1](/1)
        * [List item 2](/2)
        * [List item 3](/3)
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <bullet_list>
            <list_item>
              <paragraph>
                <pending_xref refdomain="None" refexplicit="True" reftarget="/1" reftype="any" refwarn="True">
                  <reference refuri="/1">List item 1</reference>
                </pending_xref>
              </paragraph>
            </list_item>
            <list_item>
              <paragraph>
                <pending_xref refdomain="None" refexplicit="True" reftarget="/2" reftype="any" refwarn="True">
                  <reference refuri="/2">List item 2</reference>
                </pending_xref>
              </paragraph>
            </list_item>
            <list_item>
              <paragraph>
                <pending_xref refdomain="None" refexplicit="True" reftarget="/3" reftype="any" refwarn="True">
                  <reference refuri="/3">List item 3</reference>
                </pending_xref>
              </paragraph>
            </list_item>
          </bullet_list>
        </document>
        """,
    )


def test_enumerated_list():
    assert_parses(
        """
        1. List item 1
        2. List item 2
        3. List item 3
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <enumerated_list>
            <list_item>
              <paragraph>List item 1</paragraph>
            </list_item>
            <list_item>
              <paragraph>List item 2</paragraph>
            </list_item>
            <list_item>
              <paragraph>List item 3</paragraph>
            </list_item>
          </enumerated_list>
        </document>
        """,
    )


def test_code():
    assert_parses(
        """
        Code:

            #!/bin/sh
            python
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>Code:</paragraph>
          <literal_block xml:space="preserve">#!/bin/sh
        python</literal_block>
        </document>
        """,
    )


def test_block_quote():
    assert_parses(
        """
        > Here is a quoted list:
        > \n\
        > * Item 1
        > * Item 2
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <block_quote>
            <paragraph>Here is a quoted list:</paragraph>
            <bullet_list>
              <list_item>
                <paragraph>Item 1</paragraph>
              </list_item>
              <list_item>
                <paragraph>Item 2</paragraph>
              </list_item>
            </bullet_list>
          </block_quote>
        </document>
        """,
    )


def test_horizontal_rule():
    assert_parses(
        """
        Foo

        ----

        Bar
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>Foo</paragraph>
          <transition/>
          <paragraph>Bar</paragraph>
        </document>
        """,
    )


def test_html_inline():
    assert_parses(
        """
        Foo

        <blink>Blink</blink>
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>Foo</paragraph>
          <paragraph>
            <raw format="html" xml:space="preserve">&lt;blink&gt;</raw>
            Blink
            <raw format="html" xml:space="preserve">&lt;/blink&gt;</raw>
          </paragraph>
        </document>
        """,
    )


def test_html_block():
    assert_parses(
        """
        Foo

        <div>
            <blink>Blink</blink>
        </div>
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <paragraph>Foo</paragraph>
          <raw format="html" xml:space="preserve">&lt;div&gt;
            &lt;blink&gt;Blink&lt;/blink&gt;
        &lt;/div&gt;</raw>
        </document>
        """,
    )


def test_embedded_rst_block():
    assert_parses(
        """
        ```eval_rst
        .. image:: figure.png
        ```
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <literal_block language="eval_rst" xml:space="preserve">.. image:: figure.png</literal_block>
        </document>
        """,
    )
