"""Docutils Markdown parser"""

# from markdown_checklist.extension import ChecklistExtension
# from markdown_strikethrough import StrikethroughExtension
# from mdx_unimoji import UnimojiExtension
from .depth import Depth
from docutils import parsers, nodes
from html.parser import HTMLParser
from markdown import markdown
from pydash import _
import re
import yaml

__all__ = ['MarkdownParser']

class MarkdownParser(parsers.Parser):
    """Docutils parser for Markdown"""

    depth = Depth()
    level = 0
    supported = ('md', 'markdown')
    translate_section_name = None

    def __init__(self):
        self._level_to_elem = {}

    def parse(self, inputstring, document):
        self.document = document
        self.current_node = document
        self.setup_parse(inputstring, document)
        frontmatter = self.get_frontmatter(inputstring)
        md = self.get_md(inputstring)
        html = markdown(
            md + '\n',
            extensions=[
                # ChecklistExtension(),
                # StrikethroughExtension(),
                # UnimojiExtension(),
                'extra',
                'nl2br',
                'sane_lists',
                'smarty',
                'toc',
                'wikilinks',
            ]
        )
        self.convert_html(html)
        self.finish_parse()

    def convert_html(self, html):
        html = html.replace('\n', '')

        class MyHTMLParser(HTMLParser):
            def handle_starttag(_, tag, attrs):
                attrs = self.attrs_to_dict(attrs)
                fn_name = 'visit_' + tag
                if hasattr(self, fn_name):
                    fn = getattr(self, fn_name)
                    fn(attrs)
                else:
                    self.visit_html(tag, attrs)

            def handle_endtag(_, tag):
                fn_name = 'depart_' + tag
                if hasattr(self, fn_name):
                    fn = getattr(self, fn_name)
                    fn()
                else:
                    self.depart_html(tag)

            def handle_data(_, data):
                self.visit_text(data)
                self.depart_text()

        self.visit_document()
        parser = MyHTMLParser()
        parser.feed(html)
        self.depart_document()

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

    def convert_ast(self, ast):
        for (node, entering) in ast.walker():
            fn_prefix = 'visit' if entering else 'depart'
            fn_name = '{0}_{1}'.format(fn_prefix, node.t.lower())
            fn_default = 'default_{0}'.format(fn_prefix)
            fn = getattr(self, fn_name, None)
            if fn is None:
                fn = getattr(self, fn_default)
            fn(node)

    def visit_section(self, level, attrs):
        self.descend('section')
        for i in range(self.level - level + 1):
            self.depart_section(level)
        self.level = level
        section = nodes.section()
        id_attr = attrs['id'] if 'id' in attrs else ''
        section['ids'] = id_attr
        section['names'] = id_attr
        title = nodes.title()
        setattr(self, 'title_node', title)
        section.append(title)
        self.append_node(section)

    def depart_section(self, level):
        if (self.current_node.parent):
            self.exit_node()
        self.ascend('section')

    def visit_document(self):
        self.descend('document')

    def depart_document(self):
        self.ascend('document')

    def visit_p(self, attrs):
        self.descend('p')
        if self.depth.get('html') > 0:
            self.visit_html('p', attrs)
        else:
            paragraph = nodes.paragraph()
            self.append_node(paragraph)

    def depart_p(self):
        if self.depth.get('html') > 1:
            self.depart_html('p')
        else:
            self.exit_node()
        self.ascend('p')

    def visit_del(self, attrs):
        self.descend('del')
        if self.depth.get('html') > 0:
            self.visit_html('del', attrs)
        else:
            paragraph = nodes.paragraph()
            self.append_node(paragraph)

    def depart_del(self):
        if self.depth.get('html') > 1:
            self.depart_html('del')
        else:
            self.exit_node()
        self.ascend('del')

    def visit_text(self, data):
        self.descend('text')
        text = nodes.Text(data)
        if self.depth.get('html') > 0:
            text = nodes.Text(self.current_node.children[0].astext() + data)
            self.current_node.children[0] = text
        elif hasattr(self, 'title_node') and self.title_node:
            self.title_node.append(text)
            self.title_node = text
        else:
            self.append_node(text)

    def depart_text(self):
        if self.depth.get('html') > 1:
            pass
        elif hasattr(self, 'title_node') and self.title_node:
            self.title_node = self.title_node.parent
        else:
            self.exit_node()
        self.ascend('text')

    def visit_h1(self, attrs):
        self.descend('h1')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['id']:
            self.visit_html('h1', attrs)
        else:
            self.visit_section(1, attrs)

    def depart_h1(self):
        if self.depth.get('html') > 1:
            self.depart_html('h1')
        else:
            self.title_node = None
        self.ascend('h1')

    def visit_h2(self, attrs):
        self.descend('h2')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['id']:
            self.visit_html('h2', attrs)
        else:
            self.visit_section(2, attrs)

    def depart_h2(self):
        if self.depth.get('html') > 1:
            self.depart_html('h2')
        else:
            self.title_node = None
        self.ascend('h2')

    def visit_h3(self, attrs):
        self.descend('h3')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['id']:
            self.visit_html('h3', attrs)
        else:
            self.visit_section(3, attrs)

    def depart_h3(self):
        if self.depth.get('html') > 1:
            self.depart_html('h3')
        else:
            self.title_node = None
        self.ascend('h3')

    def visit_h4(self, attrs):
        self.descend('h4')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['id']:
            self.visit_html('h4', attrs)
        else:
            self.visit_section(4, attrs)

    def depart_h4(self):
        if self.depth.get('html') > 1:
            self.depart_html('h4')
        else:
            self.title_node = None
        self.ascend('h4')

    def visit_h5(self, attrs):
        self.descend('h5')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['id']:
            self.visit_html('h5', attrs)
        else:
            self.visit_section(5, attrs)

    def depart_h5(self):
        if self.depth.get('html') > 1:
            self.depart_html('h5')
        else:
            self.title_node = None
        self.ascend('h5')

    def visit_h6(self, attrs):
        self.descend('h6')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['id']:
            self.visit_html('h6', attrs)
        else:
            self.visit_section(6, attrs)

    def depart_h6(self):
        if self.depth.get('html') > 1:
            self.depart_html('h6')
        else:
            self.title_node = None
        self.ascend('h6')

    def visit_a(self, attrs):
        self.descend('a')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['href']:
            self.visit_html('a', attrs)
        else:
            reference = nodes.reference()
            reference['refuri'] = attrs['href'] if 'href' in attrs else ''
            if self.title_node:
                self.title_node.append(reference)
                self.title_node = reference
            else:
                self.append_node(reference)

    def depart_a(self):
        if self.depth.get('html') > 1:
            self.depart_html('a')
        elif self.title_node:
            self.title_node = self.title_node.parent
        else:
            self.exit_node()
        self.ascend('a')

    def visit_img(self, attrs):
        self.descend('img')
        if self.depth.get('html') > 0 or _.keys(attrs) != ['alt', 'src']:
            self.visit_html('img', attrs)
        else:
            image = nodes.image()
            image['uri'] = attrs['src'] if 'src' in attrs else ''
            self.append_node(image)
            self.visit_text(attrs['alt'] if 'alt' in attrs else '')

    def depart_img(self):
        if self.depth.get('html') > 1:
            self.depart_html('img')
        else:
            self.depart_text()
            self.exit_node()
        self.ascend('img')

    def visit_ul(self, attrs):
        self.descend('ul')
        if self.depth.get('html') > 0 or (
            'class' in attrs and attrs['class'] == 'checklist'
        ):
            self.visit_html('ul', attrs)
        else:
            bullet_list = nodes.bullet_list()
            self.append_node(bullet_list)

    def depart_ul(self):
        if self.depth.get('html') > 1:
            self.depart_html('ul')
        else:
            self.exit_node()
        self.ascend('ul')

    def visit_ol(self, attrs):
        self.descend('ol')
        if self.depth.get('html') > 0:
            self.visit_html('ol', attrs)
        else:
            enumerated_list = nodes.enumerated_list()
            self.append_node(enumerated_list)

    def depart_ol(self):
        if self.depth.get('html') > 1:
            self.depart_html('ol')
        else:
            self.exit_node()
        self.ascend('ol')

    def visit_li(self, attrs):
        self.descend('li')
        if self.depth.get('html') > 0:
            self.visit_html('li', attrs)
        else:
            list_item = nodes.list_item()
            self.append_node(list_item)
            self.visit_p([])

    def depart_li(self):
        if self.depth.get('html') > 1:
            self.depart_html('li')
        else:
            self.depart_p()
            self.exit_node()
        self.ascend('li')

    def visit_table(self, attrs):
        self.descend('table')
        if self.depth.get('html') > 0:
            self.visit_html('table', attrs)
        else:
            table = nodes.table()
            self.append_node(table)
            tgroup = nodes.tgroup()
            self.append_node(tgroup)
            colspec = nodes.colspec()
            self.append_node(colspec)
            self.exit_node()

    def depart_table(self):
        if self.depth.get('html') > 1:
            self.depart_html('table')
        else:
            self.exit_node()
            self.exit_node()
        self.ascend('table')

    def visit_thead(self, attrs):
        self.descend('thead')
        if self.depth.get('html') > 0:
            self.visit_html('thead', attrs)
        else:
            thead = nodes.thead()
            self.append_node(thead)

    def depart_thead(self):
        if self.depth.get('html') > 1:
            self.depart_html('thead')
        else:
            self.exit_node()
        self.ascend('thead')

    def visit_tbody(self, attrs):
        self.descend('tbody')
        if self.depth.get('html') > 0:
            self.visit_html('tbody', attrs)
        else:
            tbody = nodes.tbody()
            self.append_node(tbody)

    def depart_tbody(self):
        if self.depth.get('html') > 1:
            self.depart_html('tbody')
        else:
            self.exit_node()
        self.ascend('tbody')

    def visit_tr(self, attrs):
        self.descend('tr')
        if self.depth.get('html') > 0:
            self.visit_html('tr', attrs)
        else:
            row = nodes.row()
            self.append_node(row)

    def depart_tr(self):
        if self.depth.get('html') > 1:
            self.depart_html('tr')
        else:
            self.exit_node()
        self.ascend('tr')

    def visit_th(self, attrs):
        self.descend('th')
        if self.depth.get('html') > 0:
            self.visit_html('th', attrs)
        else:
            entry = nodes.entry()
            self.append_node(entry)

    def depart_th(self):
        if self.depth.get('html') > 1:
            self.depart_html('th')
        else:
            self.exit_node()
        self.ascend('th')

    def visit_td(self, attrs):
        self.descend('td')
        if self.depth.get('html') > 0:
            self.visit_html('td', attrs)
        else:
            entry = nodes.entry()
            self.append_node(entry)

    def depart_td(self):
        if self.depth.get('html') > 1:
            self.depart_html('td')
        else:
            self.exit_node()
        self.ascend('td')

    def visit_pre(self, attrs):
        self.descend('pre')
        if self.depth.get('html') > 0:
            self.visit_html('pre', attrs)

    def depart_pre(self):
        if self.depth.get('html') > 1:
            self.depart_html('pre')
        self.ascend('pre')

    def visit_code(self, attrs):
        self.descend('code')
        if self.depth.get('html') > 0:
            self.visit_html('code', attrs)
        elif self.depth.get('p') > 0:
            literal = nodes.literal()
            self.append_node(literal)
        else:
            literal_block = nodes.literal_block()
            class_attr = attrs['class'] if 'class' in attrs else ''
            if len(class_attr):
                literal_block['language'] = class_attr
            self.append_node(literal_block)

    def depart_code(self):
        if self.depth.get('html') > 1:
            self.depart_html('code')
        else:
            self.exit_node()
        self.ascend('code')

    def visit_blockquote(self, attrs):
        self.descend('blockquote')
        if self.depth.get('html') > 0:
            self.visit_html('blockquote', attrs)
        else:
            block_quote = nodes.block_quote()
            self.append_node(block_quote)

    def depart_blockquote(self):
        if self.depth.get('html') > 1:
            self.depart_html('blockquote')
        else:
            self.exit_node()
        self.ascend('blockquote')

    def visit_hr(self, attrs):
        self.descend('hr')
        if self.depth.get('html') > 0:
            self.visit_html('hr', attrs)
        else:
            transition = nodes.transition()
            self.append_node(transition)

    def depart_hr(self):
        if self.depth.get('html') > 1:
            self.depart_html('hr')
        else:
            self.exit_node()
        self.ascend('hr')

    def visit_br(self, attrs):
        self.descend('br')
        if self.depth.get('html') > 0:
            self.visit_html('br', attrs)
        else:
            text = nodes.Text('\n')
            self.append_node(text)

    def depart_br(self):
        if self.depth.get('html') > 1:
            self.depart_html('br')
        else:
            self.exit_node()
        self.ascend('br')

    def visit_em(self, attrs):
        self.descend('em')
        if self.depth.get('html') > 0:
            self.visit_html('em', attrs)
        else:
            emphasis = nodes.emphasis()
            if self.title_node:
                self.title_node.append(emphasis)
                self.title_node = emphasis
            else:
                self.append_node(emphasis)

    def depart_em(self):
        if self.depth.get('html') > 1:
            self.depart_html('em')
        elif self.title_node:
            self.title_node = self.title_node.parent
        else:
            self.exit_node()
        self.ascend('em')

    def visit_strong(self, attrs):
        self.descend('strong')
        if self.depth.get('html') > 0:
            self.visit_html('strong', attrs)
        else:
            strong = nodes.strong()
            if self.title_node:
                self.title_node.append(strong)
                self.title_node = strong
            else:
                self.append_node(strong)

    def depart_strong(self):
        if self.depth.get('html') > 1:
            self.depart_html('strong')
        elif self.title_node:
            self.title_node = self.title_node.parent
        else:
            self.exit_node()
        self.ascend('strong')

    def visit_html(self, tag, attrs={}):
        self.descend('html')
        if self.depth.get('html') == 1:
            raw = nodes.raw()
            raw['format'] = 'html'
            self.current_node.append(raw)
            self.current_node = raw
        tag_html = '<' + tag + ''.join(
            _.map(
                attrs, lambda value, attr: ' ' + attr +
                (('="' + value + '"') if value != None else '')
            )
        ) + '>'
        if len(self.current_node.children):  # TODO: dont understand
            text = nodes.Text(
                self.current_node.children[0].astext() + tag_html
            )
            self.current_node.children[0] = text
        else:
            text = nodes.Text(tag_html)
            self.current_node.append(text)

    def depart_html(self, tag):
        text = nodes.Text(
            self.current_node.children[0].astext() + '</' + tag + '>'
        )
        self.current_node.children[0] = text
        if self.depth.get('html') == 1:
            self.current_node = self.current_node.parent
        self.ascend('html')

    def append_node(self, node):
        self.current_node += node
        self.current_node = node

    def exit_node(self):
        self.current_node = self.current_node.parent

    def ascend(self, name):
        self.depth.ascend(name)

    def descend(self, name):
        self.depth.descend(name)
