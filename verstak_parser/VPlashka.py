from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph
from docx.table import Table, _Cell

import verstak_parser


class VPlashka:
    def __init__(self, cell: _Cell = None):
        """
        Class for Plashka
        :param cell: cell of the table with content of Plashka
        """
        self.parts = []
        self.raw = cell
        if cell is not None:
            self.parse(cell)

    def __getitem__(self, item):
        return self.parts[item]

    def __setitem__(self, key, value):
        self.parts[key] = value

    def __iter__(self):
        return self.parts.__iter__()

    def __str__(self):
        lines = ["```plashka"]
        for part in self.parts:
            lines.append(str(part))
        lines.append("```")
        return "\n".join(lines)

    def to_html(self):
        """
        Get html representation
        :return: html representation
        """
        is_list = False
        html_parts = ['[hl]']
        list_type = None
        first_title = True
        for part in self.parts:
            if type(part) == verstak_parser.VParagraph:
                if part.text.strip() == "":
                    continue
                if first_title:
                    first_title = False
                    if len(part.text) <= 90:  # title should be less than 90 symbols
                        html_parts[0] = f'[hl title="{part.text}"]'
                    else:
                        html_parts.append(part.to_html(is_warning=True))
                    continue
                if part.title and str(part).strip() == "":
                    continue
                # list logic:
                # 1. First option appears and ul or ol is added
                # 2. All list options are added
                # 3. When anything but list option is got closing of ul or ol is added
                if not is_list and part.list_type is not None:
                    list_type = part.list_type
                    is_list = True
                    html_parts.append(f"{verstak_parser.VListParagraph.type_to_html(list_type)}\n")
                elif is_list and part.list_type is None:
                    html_parts[-1] += verstak_parser.VListParagraph.type_to_html(list_type, False)
                    is_list = False
                if is_list and part.list_type is not None:
                    html_parts[-1] += f"{part.to_html()}\n"
                    continue
            elif is_list:
                html_parts[-1] += verstak_parser.VListParagraph.type_to_html(list_type, False)
                is_list = False
            html_parts.append(part.to_html())
        if is_list:  # List can end at the end of the document so it should be closed
            html_parts[-1] += verstak_parser.VListParagraph.type_to_html(list_type, False)
        html_parts.append("[/hl]")
        return "\n".join(html_parts)

    def do_typograf(self):
        """
        Rework text of parts by rules from typograph
        :return: resulted text
        """
        for part in self:
            part.do_typograf()

    def parse(self, cell: _Cell) -> []:
        """
        Parce cell of the Table with Plashka
        :param cell: cell of a table
        :return: resulted parts of the Plashka
        """
        for elem in cell._element:
            if type(elem) == CT_P:
                self.parts.append(verstak_parser.VParagraph((Paragraph(elem, cell))))
            elif type(elem) == CT_Tbl:
                self.parts.extend(verstak_parser.VTable(Table(elem, cell)).items)
        return self.parts
