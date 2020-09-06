import os
import docx
from typing import Optional
from docx.document import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph
from docx.table import Table

from .VParagraph import VParagraph
from .VText import VText
from .VPicture import VPicture
from .VTable import VTable


class VDocument:
    def __init__(self, document: Document = None):
        self.first_table = None
        self.first_title = None
        self.raw = document
        self.parts = []
        if document is not None:
            self.parse(document)

    def __parse_paragraph(self, element: CT_P, document: Document, caption: bool) -> Optional[VParagraph]:
        paragraph = VParagraph(Paragraph(element, document))
        if self.first_title is None and paragraph.title:
            self.first_title = paragraph
            return None
        if not caption or paragraph.is_picture():
            return paragraph
        elif type(paragraph[0]) == VText and paragraph.title:
            return paragraph
        elif str(paragraph) != "":
            imgs_count = 0
            for part in reversed(self.parts):
                if type(part) == VParagraph and part.is_picture():
                    imgs_count += 1
                else:
                    break
            for ppart in self.parts[-imgs_count]:
                if type(ppart) == VPicture:
                    ppart: VPicture
                    ppart.caption = str(paragraph)
                    break
        return None

    def __parse_table(self, element: CT_Tbl, document: Document):
        if self.first_table is None:
            self.first_table = VTable(Table(element, document))
            return None
        table = VTable(Table(element, document))
        self.parts.append(table)
        if len(self.parts) > 1 and table.type == VTable.TYPE.BIG_TABLE:
            if type(self.parts[-2]) == VParagraph:
                self.parts[-2].title = True
                self.parts[-2].title_level = 2

    def parse(self, document: Document):
        self.raw = document
        blank_line_caption_found = False
        caption = False
        for elem in document.element.body:
            if type(elem) == CT_P:
                paragraph = self.__parse_paragraph(elem, self.raw, caption)
                if paragraph is None:
                    caption = False
                elif caption and str(paragraph).strip() == "" and not blank_line_caption_found:
                    blank_line_caption_found = True
                    continue
                elif paragraph.is_picture():
                    caption = True
                if paragraph is not None:
                    self.parts.append(paragraph)
            elif type(elem) == CT_Tbl:
                self.__parse_table(elem, self.raw)
            blank_line_caption_found = False
        return self.parts

    def store_markdown(self, path: str = f"markdown{os.sep}result.md"):
        with open(path, "w") as result_file:
            for line in [str(x) for x in self.parts]:
                result_file.write(f"{line}\n")
            result_file.flush()

    @staticmethod
    def from_file(doc_path: str):
        document: Document = docx.Document(doc_path)
        return VDocument(document)
