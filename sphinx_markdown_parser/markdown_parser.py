"""Docutils Markdown parser"""

from collections import OrderedDict

from docutils import parsers, nodes
import markdown
from markdown import util

from pydash import _
import re
import yaml

__all__ = ['MarkdownParser']

TAGS_INLINE = set("""
b, big, i, small, tt
abbr, acronym, cite, code, dfn, em, kbd, strong, samp, var
a, bdo, br, img, map, object, q, script, span, sub, sup
button, input, label, select, textarea
""".replace(",","").split())
INVALID_ANCHOR_CHARS = re.compile("[^-_:.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]")

def to_html_anchor(s):
    if not s:
        return s
    if not s[0].isalpha():
        s = "-" + s
    return INVALID_ANCHOR_CHARS.sub("-", s.lower())

IGNORE_ALL_CHILDREN = object()


class Markdown(markdown.Markdown):

    def parse(self, source):
        """
        Like super.convert() but returns the parse tree instead of doing
        postprocessing.
        """

        # Fixup the source text
        if not source.strip():
            return ''  # a blank unicode string

        try:
            source = util.text_type(source)
        except UnicodeDecodeError as e:  # pragma: no cover
            # Customise error message while maintaining original trackback
            e.reason += '. -- Note: Markdown only accepts unicode input!'
            raise

        # Split into lines and run the line preprocessors.
        self.lines = source.split("\n")
        for prep in self.preprocessors:
            self.lines = prep.run(self.lines)

        # Parse the high-level elements.
        root = self.parser.parseDocument(self.lines).getroot()

        # Run the tree-processors
        for treeprocessor in self.treeprocessors:
            newRoot = treeprocessor.run(root)
            if newRoot is not None:
                root = newRoot

        return root

class MarkdownParser(parsers.Parser):
    """Docutils parser for Markdown"""

    supported = ('md', 'markdown')
    translate_section_name = None

    default_config = {
        'extensions': []
    }

    def __init__(self):
        self._level_to_elem = {}

    def parse(self, inputstring, document):
        self.document = document
        self.current_node = document
        self.config = self.default_config.copy()
        try:
            new_cfg = self.document.settings.env.config.markdown_parser_config
            self.config.update(new_cfg)
        except AttributeError:
            pass
        self.setup_parse(inputstring, document)
        frontmatter = self.get_frontmatter(inputstring)

        self.md = Markdown(extensions=self.config.get('extensions'))
        tree = self.md.parse(self.get_md(inputstring) + "\n")
        self.prep_raw_html()

        # the stack for depth-traverse-reading the markdown AST tree
        self.parse_stack_r = []
        # the stack for depth-traverse-writing the docutils AST tree
        self.parse_stack_w = [self.current_node]
        # the stack for determining nested sections
        self.parse_stack_h = [0]
        # index into parse_stack_w used for special cases where one markdown
        # node might generate more than one docutils node, e.g.
        # <h1> -> <section><title> in start_new_section
        self.parse_stack_w_old = 1
        self.walk_markdown_ast(tree)
        #text = self.current_node.pformat()
        #print("result:: ==== ")
        #print(text[:min(len(text), text.find("<title>") + 200)])
        #print("end result")

        self.finish_parse()

    def get_frontmatter(self, string):
        frontmatter = {}
        frontmatter_string = ''
        frontmatter_regex = re.findall(r'^\s*---+((\s|\S)+?)---+', string)
        if len(frontmatter_regex) and len(frontmatter_regex[0]):
            frontmatter_string = frontmatter_regex[0][0]
        if len(frontmatter_string):
            frontmatter = yaml.load(frontmatter_string)
        return frontmatter

    def get_md(self, string):
        return re.sub(r'^\s*---+(\s|\S)+?---+\n((\s|\S)*)', r'\2', string)

    def attrs_to_dict(self, attrs):
        attrs_dict = {}
        for item in attrs:
            if len(item) == 2:
                attrs_dict[item[0]] = item[1]
        return attrs_dict

    def prep_raw_html(self):
        # code adapted from markedown.core.RawHtmlPostprocessor
        replacements = OrderedDict()
        for i in range(self.md.htmlStash.html_counter):
            html = self.md.htmlStash.rawHtmlBlocks[i]
            if self.isblocklevel(html):
                replacements["<p>%s</p>" %
                             (self.md.htmlStash.get_placeholder(i))] = \
                    html + "\n"
            replacements[self.md.htmlStash.get_placeholder(i)] = html
        self.raw_html = replacements
        if replacements:
            self.raw_html_k = re.compile("(" + "|".join(re.escape(k) for k in self.raw_html) + ")")
        else:
            self.raw_html_k = None

    def isblocklevel(self, html):
        m = re.match(r'^\<\/?([^ >]+)', html)
        if m:
            if m.group(1)[0] in ('!', '?', '@', '%'):
                # Comment, php etc...
                return True
            return self.md.is_block_level(m.group(1))
        return False

    def walk_markdown_ast(self, node):
        n = node.tag.lower()
        self.parse_stack_w_old = len(self.parse_stack_w)
        r_depth = len(self.parse_stack_r)
        self.parse_stack_w_old = len(self.parse_stack_w)

        res = self.dispatch(True, n, node)
        if res is IGNORE_ALL_CHILDREN:
            return
        # shortcut for pushing one item so visitors don't have to
        if res is not None and res != self.parse_stack_w[-1]:
            self.append_node(res)
        # add text
        if node.text and node.text.strip():
            self.append_text(node.text)

        # dispatch might have modified parse_stack_w_old, so read it again
        w_depth = self.parse_stack_w_old

        # set stacks and recurse
        self.current_node = self.parse_stack_w[-1]
        self.parse_stack_r.append(node)
        for chd in node.getchildren():
            self.walk_markdown_ast(chd)
        self.parse_stack_r.pop()
        assert r_depth == len(self.parse_stack_r)
        # restore previous write stack
        self.parse_stack_w = self.parse_stack_w[:w_depth]
        self.current_node = self.parse_stack_w[-1]
        assert w_depth == len(self.parse_stack_w)

        self.dispatch(False, n, node, res)
        # add text
        if node.tail and node.tail.strip():
            self.append_text(node.tail)

    def dispatch(self, entering, n, *args):
        fn_prefix = "visit" if entering else "depart"
        fn_name = "{0}_{1}".format(fn_prefix, n)
        def x(*args): return self.dispatch_default(entering, *args)
        return getattr(self, fn_name, x)(*args)

    def dispatch_default(self, entering, node, *args):
        if entering:
            raise NotImplementedError("markdown_parser not implemented for <%s>: %s" % (node.tag, node.text))
            # below is for debugging, uncomment prev line to activate
            print(" " * len(self.parse_stack_r) * 2, node.tag, node.text[:40] if node.text else "")

    def append_text(self, text):
        if not self.raw_html_k:
            self.parse_stack_w[-1] += nodes.Text(text)
            return
        parts = self.raw_html_k.split(text)
        sep = False
        for p in parts:
            if sep:
                raw = nodes.raw()
                raw['format'] = 'html'
                raw += nodes.Text(self.raw_html[p])
                self.parse_stack_w[-1] += raw
            else:
                self.parse_stack_w[-1] += nodes.Text(p)
            sep = not sep

    def append_node(self, node):
        self.parse_stack_w[-1] += node
        self.parse_stack_w.append(node)
        return node

    def new_section(self, heading):
        section = nodes.section()
        section['ids'] = [to_html_anchor("".join(heading.itertext()))]
        return section

    def start_new_section(self, lvl, heading):
        if lvl > self.parse_stack_h[-1]:
            self.append_node(self.new_section(heading))
        elif lvl == self.parse_stack_h[-1]:
            x = self.parse_stack_w.pop()
            assert isinstance(x, nodes.section) or isinstance(x, nodes.document)
            self.append_node(self.new_section(heading))
        elif lvl < self.parse_stack_h[-1]:
            x = self.parse_stack_w.pop()
            assert isinstance(x, nodes.section) or isinstance(x, nodes.document)
            x = self.parse_stack_w.pop()
            assert isinstance(x, nodes.section) or isinstance(x, nodes.document)
            self.append_node(self.new_section(heading))
        # don't rewind past this, when departing the <hn> tag
        self.parse_stack_w_old = len(self.parse_stack_w)
        self.parse_stack_h.append(lvl)
        assert isinstance(self.parse_stack_w[-1], nodes.section)
        return nodes.title()

    def visit_script(self, node):
        return IGNORE_ALL_CHILDREN

    def visit_p(self, node):
        return nodes.paragraph()

    def visit_span(self, node):
        if "MathJax_Preview" in node.attrib.get("class", "").split():
            self.parse_stack_w[-1] += nodes.Text("$")
            return None
        return None

    def depart_span(self, node, _):
        if "MathJax_Preview" in node.attrib.get("class", "").split():
            self.parse_stack_w[-1] += nodes.Text("$")
            return None
        return None

    def visit_div(self, node):
        if len(self.parse_stack_w) == 1:
            # top-level, ignore
            return None
        if "MathJax_Preview" in node.attrib.get("class", "").split():
            self.parse_stack_w[-1] += nodes.Text("$$")
            return None
        return nodes.paragraph()

    def depart_div(self, node, _):
        if "MathJax_Preview" in node.attrib.get("class", "").split():
            self.parse_stack_w[-1] += nodes.Text("$$")
            return None

    def visit_h1(self, node):
        return self.start_new_section(1, node)

    def visit_h2(self, node):
        return self.start_new_section(2, node)

    def visit_h3(self, node):
        return self.start_new_section(3, node)

    def visit_h4(self, node):
        return self.start_new_section(4, node)

    def visit_h5(self, node):
        return self.start_new_section(5, node)

    def visit_h6(self, node):
        return self.start_new_section(6, node)

    def visit_strong(self, node):
        return nodes.strong()

    def visit_em(self, node):
        return nodes.emphasis()

    def visit_br(self, node):
        return nodes.Text('\n')

    def visit_a(self, node):
        reference = nodes.reference()
        href = node.attrib.get('href', '')
        if href.endswith(".md"):
            href = href[:-3] + ".html"
        reference['refuri'] = href
        return reference

    def visit_ol(self, node):
        return nodes.enumerated_list()

    def visit_ul(self, node):
        return nodes.bullet_list()

    def visit_li(self, node):
        ch = node.getchildren()
        # extra "paragraph" is needed to avoid breaking docutils assumptions
        if not ch or ch[0].tag in TAGS_INLINE:
            self.append_node(nodes.list_item())
            return nodes.paragraph()
        else:
            return nodes.list_item()

    def visit_img(self, node):
        image = nodes.image()
        image['uri'] = node.attrib.get('src', '')
        image['alt'] = node.attrib.get('alt', '')
        return image

    def visit_hr(self, node):
        return nodes.transition()

    def visit_blockquote(self, node):
        return nodes.block_quote()

    def visit_table(self, node):
        # pymarkdown does not generate these but docutils expects them
        table = nodes.table()
        table['classes'] = ["colwidths-auto"]
        self.append_node(table)
        tgroup = nodes.tgroup()
        # the below hack is needed because docutils expects colspecs
        # ideally we would find the actual number of columns of the table but
        # i couldn't be bothered writing the code
        for _ in len(node.iter()):
            tgroup += nodes.colspec()
        tgroup['stub'] = None
        return tgroup

    def visit_thead(self, node):
        return nodes.thead()

    def visit_tbody(self, node):
        return nodes.tbody()

    def visit_tr(self, node):
        return nodes.row()

    def visit_th(self, node):
        return nodes.entry()

    def visit_td(self, node):
        return nodes.entry()

    def visit_code(self, node):
        return nodes.literal()

    def visit_pre(self, node):
        return nodes.literal_block()
