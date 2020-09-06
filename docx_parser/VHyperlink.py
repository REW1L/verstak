from lxml.etree import _Element
from docx.opc.rel import _Relationship
from docx.text.paragraph import Paragraph


class VHyperlink:
    def __init__(self, hyperlink: _Element = None, paragraph: Paragraph = None):
        self.url = ""
        self.text = ""
        self.raw = hyperlink
        if hyperlink is not None:
            self.parse(hyperlink, paragraph)

    def __str__(self):
        return f"[{self.text}]( {self.url} )"

    def parse(self, hyperlink: _Element, paragraph: Paragraph):
        url_id = None
        if len(hyperlink.values()) > 0:
            url_id = hyperlink.values()[0]
        url: _Relationship = paragraph.part.rels[url_id]
        self.url = url.target_ref
        self.text = hyperlink[0].text
        self.raw = hyperlink
        return str(self)
