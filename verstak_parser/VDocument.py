import os
import docx
from tqdm import tqdm
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
from .VBigTable import VBigTable

class VDocument:
    def __init__(self, document: Document = None):
        """
        Class for docx document
        :param document: raw docx document
        """
        self.first_table = None
        self.first_title = None
        self.raw = document
        self.parts = []
        if document is not None:
            self.parse(document)

    def __parse_paragraph(self, element: CT_P, document: Document, caption: bool) -> Optional[VParagraph]:
        """
        Parse CT_P element from docx document
        :param element: CT_P from document
        :param document: current docx.document.Document object
        :param caption: parse CT_P as caption for picture
        :return: VParagraph or None if recognition is failed or caption is applied to previous parts
        """
        paragraph = VParagraph(Paragraph(element, document))
        if not self.first_title and len(self.parts) > 0:  # first title is absent in document
            self.first_title = False
        if self.first_title is None and paragraph.title:  # first title in the document should be skipped
            self.first_title = paragraph
            return None
        if not caption or paragraph.is_picture():
            return paragraph
        elif type(paragraph[0]) == VText and paragraph.title:
            return paragraph
        elif str(paragraph) != "":  # paragraph should have at least one symbol
            imgs_count = 0
            # caption should be applied to the first picture in a sequence
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
        """
        Parse CT_Tbl from document and add VTabel to self.parts
        :param element: CT_Tbl from document
        :param document: current docx.document.Document object
        :return: None
        """
        if self.first_table is None:  # the first table in a document should be skipped
            self.first_table = VTable(Table(element, document))
            return None
        table = VTable(Table(element, document))
        self.parts.append(table)
        if len(self.parts) > 1 and table.type == VTable.TYPE.BIG_TABLE:
            if type(self.parts[-2]) == VParagraph:
                self.parts[-2].title = True
                self.parts[-2].title_level = 2

    def parse(self, document: Document) -> list:
        """
        Parse docx document
        :param document: a docx document to parse
        :return: parts of the resulted document
        """
        self.raw = document
        blank_line_caption_found = False
        caption = False
        for elem in tqdm(document.element.body):
            if type(elem) == CT_P:
                paragraph = self.__parse_paragraph(elem, self.raw, caption)
                if paragraph is None:
                    caption = False
                elif caption and str(paragraph).strip() == "" and not blank_line_caption_found:
                    blank_line_caption_found = True
                    continue
                elif paragraph.is_picture():
                    caption = True
                elif paragraph.title:
                    caption = False
                if paragraph is not None:
                    self.parts.append(paragraph)
            elif type(elem) == CT_Tbl:
                self.__parse_table(elem, self.raw)
            blank_line_caption_found = False
        return self.parts

    def __split_paragraphs(self):
        """
        Split paragraphs by new lines
        """
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

    def to_html(self, allow_header_links: bool = False, skip_tables: bool = False) -> str:
        """
        Get html representation
        :param allow_header_links: allows links to be added for headers/titles
        :param skip_tables: adds stub instead of big tables
        :return: html representation
        """
        html_parts = []
        is_list = False
        list_type = None
        self.__split_paragraphs()
        for part in self.parts:
            if type(part) == VParagraph:
                if part.text.strip() == "":
                    continue
                # list logic:
                # 1. First option appears and ul or ol is added
                # 2. All list options are added
                # 3. When anything but list option is got closing of ul or ol is added
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
                    # the table title should be h3 with class table-heading
                    if len(html_parts) > 0 and html_parts[-1].startswith("<h2>"):
                        html_parts[-1] = html_parts[-1].replace("<h2>", '<h3 class="table-heading">')
                        html_parts[-1] = html_parts[-1].replace("</h2>", '</h3>')
                    html_parts.append(part.to_html(skip_tables))
                else:
                    html_parts.append(part.to_html())
            elif type(part) in [VParagraph, VPlashka]:  # VPlashka has headers in it
                html_parts.append(part.to_html(allow_header_links=allow_header_links))
            else:
                html_parts.append(part.to_html())
        if is_list:  # List can end at the end of the document so it should be closed
            html_parts[-1] += VListParagraph.type_to_html(list_type, False)
        return "\n\n".join(html_parts)  # it should be an empty line between parts of the document

    def do_typograf(self):
        """
        Rework text by rules from typograph
        """
        for part in self.parts:
            part.do_typograf()

    def store_html(self, path: str = f"html{os.sep}result.html", allow_header_links: bool = False,
                   skip_tables: bool = False):
        """
        Store document as file with html structure
        :param path: output file path
        :param allow_header_links: allows links to be added for headers/titles
        :param skip_tables: adds stub instead of big tables
        """
        with open(path, "w") as result_file:
            result_file.write(self.to_html(allow_header_links=allow_header_links, skip_tables=skip_tables))
            result_file.write("\n")
            result_file.flush()

    def store_markdown(self, path: str = f"markdown{os.sep}result.md"):
        """
        Store document as file with markdown structure
        :param path: output file path
        """
        with open(path, "w") as result_file:
            for line in [str(x) for x in self.parts]:
                result_file.write(f"{line}\n")
            result_file.flush()

    @staticmethod
    def from_file(doc_path: str):
        """
        Get VDocument from docx file
        :param doc_path: docx file path
        :return: resulted VDocument
        """
        document: Document = docx.Document(doc_path)
        return VDocument(document)
