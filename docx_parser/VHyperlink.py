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
        if self.text.endswith(" "):
            return f"[{self.text[:-1]}]( {self.url} ) "
        else:
            return f"[{self.text}]( {self.url} )"

    def to_html(self):
        if len([x for x in self.url if x == "(" or x == ")"]) == 0:
            if self.text.endswith(" "):
                return f"{{{self.text[:-1]}}}({self.url}) "
            else:
                return f"{{{self.text}}}({self.url})"
        else:
            if self.text.endswith(" "):
                return f'<a href="{self.url}" target="_blank">{self.text[:-1]}</a> '
            else:
                return f'<a href="{self.url}" target="_blank">{self.text}</a>'

    def parse(self, hyperlink: _Element, paragraph: Paragraph):
        url_id = None
        if len(hyperlink.values()) > 0:
            url_id = hyperlink.values()[0]
        url: _Relationship = paragraph.part.rels[url_id]
        self.url = url.target_ref
        self.text = hyperlink[0].text
        self.raw = hyperlink
        return str(self)
