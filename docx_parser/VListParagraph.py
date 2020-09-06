from enum import Enum
from docx.oxml.numbering import CT_NumPr
from docx.oxml.text.parfmt import CT_PPr
from docx.text.paragraph import Paragraph


class VListParagraph:
    class Type(Enum):
        NONE = 0
        NUMERIC = 1
        BULLET = 2
        ABC = 3

    def __init__(self, list_text: CT_PPr = None, paragraph: Paragraph = None):
        self.text = ""
        self.level = 0
        self.type = VListParagraph.Type.NONE
        self.raw = list_text
        if list_text is not None:
            self.parse(list_text, paragraph)

    def __str__(self):
        level = "  " * self.level
        if self.type == VListParagraph.Type.NUMERIC:
            list_str = "1. "
        else:
            list_str = "- "
        return f"{level}{list_str}{self.text}"

    def parse(self, list_text: CT_PPr, paragraph: Paragraph) -> str:
        self.raw = paragraph
        option: CT_NumPr = list_text.numPr
        self.text = paragraph.text
        self.level = option.ilvl.val
        if paragraph.text.strip()[0].isupper() and paragraph.text.strip().endswith("."):
            self.type = VListParagraph.Type.NUMERIC
        else:
            self.type = VListParagraph.Type.BULLET
        return str(self)
