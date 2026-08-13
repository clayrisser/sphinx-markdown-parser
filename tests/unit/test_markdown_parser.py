"""AST-level tests for MarkdownParser."""

from __future__ import annotations

from textwrap import dedent

from docutils.utils import new_document

from sphinx_markdown_parser.parser import MarkdownParser

default_test_config = {
    "extensions": [
        "extra",
        "nl2br",
        "sane_lists",
        "smarty",
        "toc",
        "wikilinks",
    ]
}


def assert_parses(source, expected):
    parser = MarkdownParser(config=default_test_config)
    parser.parse(dedent(source), new_document("<string>"))
    actual = dedent(parser.document.asdom().toprettyxml(indent="  "))
    assert actual == dedent(expected).lstrip()


def test_frontmatter():
    assert_parses(
        """
        ---
        author: Ada Lovelace
        tags: docs
        ---

        # Title
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <docinfo>
            <field>
              <field_name>author</field_name>
              <field_body>
                <paragraph>Ada Lovelace</paragraph>
              </field_body>
            </field>
            <field>
              <field_name>tags</field_name>
              <field_body>
                <paragraph>docs</paragraph>
              </field_body>
            </field>
          </docinfo>
          <section ids="title" names="title">
            <title id="title">Title</title>
          </section>
        </document>
        """,
    )


def test_kitchen_sink():
    assert_parses(
        """
        ----
        hello: world
        ----

        # I

        ```py
        hello = 'world'
        ```

        ## _[**A**](https://google.com)_

        > some-blockquote

        [google](https://www.google.com)

        [local page](page.md#heading)

        ## [B](#b)

        ### level 3

        #### level 4

        ## level 2

        ![ello](some-image.img)

        * one
        * two

        1. ONE
        2. TWO

        _italicize_

        **bold**

        <strong attr="some-attr">special</strong>

        code `<> &amp;` code

        ```
        <> &amp;
        ```

        ---

        | one | two |
        | --- | --- |
        | ONE | TWO |

        <video hello="world"><boo>howdy</boo></video>

        wow
        """,
        """
        <?xml version="1.0" ?>
        <document source="&lt;string&gt;">
          <docinfo>
            <field>
              <field_name>hello</field_name>
              <field_body>
                <paragraph>world</paragraph>
              </field_body>
            </field>
          </docinfo>
          <section ids="i" names="i">
            <title id="i">I</title>
            <literal_block language="py" xml:space="preserve">hello = 'world'</literal_block>
            <section ids="a" names="a">
              <title id="a">
                <emphasis>
                  <reference refuri="https://google.com">
                    <strong>A</strong>
                  </reference>
                </emphasis>
              </title>
              <block_quote>
                <paragraph>some-blockquote</paragraph>
              </block_quote>
              <paragraph>
                <reference refuri="https://www.google.com">google</reference>
              </paragraph>
              <paragraph>
                <reference refuri="page.html#heading">local page</reference>
              </paragraph>
            </section>
            <section ids="b" names="b">
              <title id="b">
                <reference refuri="#b">B</reference>
              </title>
              <section ids="level-3" names="level-3">
                <title id="level-3">level 3</title>
                <section ids="level-4" names="level-4">
                  <title id="level-4">level 4</title>
                </section>
              </section>
            </section>
            <section ids="level-2" names="level-2">
              <title id="level-2">level 2</title>
              <paragraph>
                <image uri="some-image.img">ello</image>
              </paragraph>
              <bullet_list>
                <list_item>
                  <paragraph>one</paragraph>
                </list_item>
                <list_item>
                  <paragraph>two</paragraph>
                </list_item>
              </bullet_list>
              <enumerated_list>
                <list_item>
                  <paragraph>ONE</paragraph>
                </list_item>
                <list_item>
                  <paragraph>TWO</paragraph>
                </list_item>
              </enumerated_list>
              <paragraph>
                <emphasis>italicize</emphasis>
              </paragraph>
              <paragraph>
                <strong>bold</strong>
              </paragraph>
              <paragraph>
                <raw format="html" xml:space="preserve">&lt;strong attr=&quot;some-attr&quot;&gt;special&lt;/strong&gt;</raw>
              </paragraph>
              <paragraph>
                code 
                <literal>&lt;&gt; &amp;amp;</literal>
                 code
              </paragraph>
              <literal_block xml:space="preserve">&lt;&gt; &amp;amp;
        </literal_block>
              <transition/>
              <table classes="colwidths-auto">
                <tgroup stub="None">
                  <colspec/>
                  <colspec/>
                  <thead>
                    <row>
                      <entry>
                        <paragraph>one</paragraph>
                      </entry>
                      <entry>
                        <paragraph>two</paragraph>
                      </entry>
                    </row>
                  </thead>
                  <tbody>
                    <row>
                      <entry>
                        <paragraph>ONE</paragraph>
                      </entry>
                      <entry>
                        <paragraph>TWO</paragraph>
                      </entry>
                    </row>
                  </tbody>
                </tgroup>
              </table>
              <raw format="html" xml:space="preserve">&lt;video hello=&quot;world&quot;&gt;&lt;boo&gt;howdy&lt;/boo&gt;&lt;/video&gt;
        </raw>
              <paragraph>wow</paragraph>
            </section>
          </section>
        </document>
        """,
    )
