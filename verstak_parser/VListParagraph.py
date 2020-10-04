from enum import Enum
from docx.oxml.numbering import CT_NumPr
from docx.oxml.text.parfmt import CT_PPr
from docx.text.paragraph import Paragraph

from .VText import VText


class VListParagraph(VText):
    class Type(Enum):
        NONE = 0
        NUMERIC = 1
        BULLET = 2
        ABC = 3

    @staticmethod
    def type_to_html(list_type: Type, opening: bool = True):
        """
        Get html representation of list type
        :param list_type: type of list
        :param opening: True to get open tag otherwise get close tag
        :return: open or closed tag for list type
        """
        if list_type == VListParagraph.Type.BULLET:
            if opening:
                ending = "ul]"
            else:
                ending = "ul]"
        else:
            if opening:  # define all ordered lists as common ordered list
                ending = "ol type=milchin]"
            else:
                ending = "ol]"
        if opening:
            return f"[{ending}"
        else:
            return f"[/{ending}"

    def __init__(self, list_text: CT_PPr = None, paragraph: Paragraph = None):
        """
        Class for part of paragraph with list representation
        :param list_text: docx part with list
        :param paragraph: docx paragraph which relates to list
        """
        super(VListParagraph, self).__init__()
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
        return f"{level}{list_str}"

    def to_html(self):
        """
        Get html representation
        :return: empty line because all text is included in other parts of paragraphs
        """
        return ""

    def parse(self, list_text: CT_PPr, paragraph: Paragraph) -> str:
        """
        Parse raw list part of docx paragraph
        :param list_text: part of docx paragraph with list options
        :param paragraph: docx paragraph which relates to list
        :return: text representation
        """
        self.raw = paragraph
        option: CT_NumPr = list_text.numPr
        self.text = paragraph.text
        self.level = option.ilvl.val
        strip_text = paragraph.text.strip()
        if strip_text != "" and strip_text[0].isupper() and strip_text.endswith("."):
            self.type = VListParagraph.Type.NUMERIC
        else:
            self.type = VListParagraph.Type.BULLET
        return str(self)
