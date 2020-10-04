from lxml.etree import _Element
from docx.opc.rel import _Relationship
from docx.text.paragraph import Paragraph

from .VText import VText


class VHyperlink(VText):
    def __init__(self, hyperlink: _Element = None, paragraph: Paragraph = None):
        """
        Class for links in docx
        :param hyperlink: <hyperlink> element from paragraph
        :param paragraph: any paragraph from document to get url of link while parsing
        """
        super(VHyperlink, self).__init__()
        self.url = ""
        self.raw = hyperlink
        if hyperlink is not None:
            self.parse(hyperlink, paragraph)

    def __str__(self):
        if self.text.endswith(" "):
            return f"[{self.text[:-1]}]( {self.url} ) "
        else:
            return f"[{self.text}]( {self.url} )"

    def to_html(self):
        """
        Get html representation
        :return: html representation
        """
        if len([x for x in self.url if x == "(" or x == ")"]) == 0:
            if self.text.endswith(" "):
                return f"{{{self.text[:-1]}}}({self.url}) "
            else:
                return f"{{{self.text}}}({self.url})"
        else:
            warning = ""
            if self.glue_warning:  # should be set if something is wrong with typograph
                warning = ' class="verstak_glue_warning"'
            if self.text.endswith(" "):
                return f'<a href="{self.url}" target="_blank"{warning}>{self.text[:-1]}</a> '
            else:
                return f'<a href="{self.url}" target="_blank"{warning}>{self.text}</a>'

    def parse(self, hyperlink: _Element, paragraph: Paragraph):
        """
        Parse <hyperlink> element from docx paragraph
        :param hyperlink: <hyperlink> element from docx paragraph
        :param paragraph: any paragraph with parent as document to get urls from
        :return: Markdown representation
        """
        url_id = None
        if len(hyperlink.values()) > 0:
            url_id = hyperlink.values()[0]
        url: _Relationship = paragraph.part.rels[url_id]
        self.url = url.target_ref
        self.text = hyperlink[0].text
        self.raw = hyperlink
        return str(self)
