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
from .VListParagraph import VListParagraph
from .VPlashka import VPlashka


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
        if not self.first_title and len(self.parts) > 0:
            self.first_title = False
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
                    ppart.caption = paragraph
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

    def __split_paragraphs(self):
        split_index = -1
        for index in range(len(self.parts)):
            if type(self.parts[index]) == VParagraph and self.parts[index].list_type is None:
                if self.parts[index].find_new_lines() != -1:
                    split_index = index
                    break
        if split_index != -1:
            index = self.parts[split_index].find_new_lines()
            if len(self.parts[split_index].parts) == index - 1:
                return
            new_texts = self.parts[split_index][index].text.split("\n")
            first_paragraph = VParagraph()
            first_paragraph.parts = self.parts[split_index][:index]
            second_paragraph = VParagraph()
            second_paragraph.parts = self.parts[split_index][index:]
            first_paragraph.parts.extend([VText(x) for x in new_texts[:-1]])
            second_paragraph.parts[0] = VText(new_texts[-1])
            parts = self.parts[:split_index]
            parts.append(first_paragraph)
            parts.append(second_paragraph)
            if len(self.parts) > split_index + 1:
                parts.extend(self.parts[split_index+1:])
            self.parts = parts
            self.__split_paragraphs()

    def to_html(self, allow_header_links: bool = False):
        html_parts = []
        is_list = False
        list_type = None
        self.__split_paragraphs()
        for part in self.parts:
            if type(part) == VParagraph:
                if part.text.strip() == "":
                    continue
                if not is_list and part.list_type is not None:
                    list_type = part.list_type
                    is_list = True
                    html_parts.append(f"{VListParagraph.type_to_html(list_type)}\n")
                elif is_list and part.list_type is None:
                    html_parts[-1] += VListParagraph.type_to_html(list_type, False)
                    is_list = False
                if is_list and part.list_type is not None:
                    html_parts[-1] += f"{part.to_html()}\n"
                    continue
            elif is_list:
                html_parts[-1] += VListParagraph.type_to_html(list_type, False)
                is_list = False
            if type(part) == VTable:
                if part.type == VTable.TYPE.BIG_TABLE:
                    if len(html_parts) > 0 and html_parts[-1].startswith("<h2>"):
                        html_parts[-1] = html_parts[-1].replace("<h2>", '<h3 class="table-heading">')
                        html_parts[-1] = html_parts[-1].replace("</h2>", '</h3>')
            if type(part) in [VParagraph, VPlashka]:
                html_parts.append(part.to_html(allow_header_links=allow_header_links))
            else:
                html_parts.append(part.to_html())
        if is_list:
            html_parts[-1] += VListParagraph.type_to_html(list_type, False)
        return "\n\n".join(html_parts)

    def do_typograf(self):
        for part in self.parts:
            part.do_typograf()

    def store_html(self, path: str = f"html{os.sep}result.html", allow_header_links: bool = False):
        with open(path, "w") as result_file:
            result_file.write(self.to_html(allow_header_links=allow_header_links))
            result_file.write("\n")
            result_file.flush()

    def store_markdown(self, path: str = f"markdown{os.sep}result.md"):
        with open(path, "w") as result_file:
            for line in [str(x) for x in self.parts]:
                result_file.write(f"{line}\n")
            result_file.flush()

    @staticmethod
    def from_file(doc_path: str):
        document: Document = docx.Document(doc_path)
        return VDocument(document)
