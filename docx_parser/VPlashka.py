from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph
from docx.table import Table, _Cell

import docx_parser


class VPlashka:
    def __init__(self, cell: _Cell = None):
        self.parts = []
        self.raw = cell
        if cell is not None:
            self.parse(cell)

    def __getitem__(self, item):
        return self.parts[item]

    def __setitem__(self, key, value):
        self.parts[key] = value

    def __iter__(self):
        return self.parts

    def __str__(self):
        lines = ["```plashka"]
        for part in self.parts:
            lines.append(str(part))
        lines.append("```")
        return "\n".join(lines)

    def to_html(self):
        is_list = False
        html_parts = ['[hl]']
        list_type = None
        first_title = True
        for part in self.parts:
            if type(part) == docx_parser.VParagraph:
                if part.text.strip() == "":
                    continue
                if first_title:
                    first_title = False
                    html_parts[0] = f'[hl title="{part.text}"]'
                    continue
                if part.title and str(part).strip() == "":
                    continue
                if not is_list and part.list_type is not None:
                    list_type = part.list_type
                    is_list = True
                    html_parts.append(f"{docx_parser.VListParagraph.type_to_html(list_type)}\n")
                elif is_list and part.list_type is None:
                    html_parts[-1] += docx_parser.VListParagraph.type_to_html(list_type, False)
                    is_list = False
                if is_list and part.list_type is not None:
                    html_parts[-1] += f"{part.to_html()}\n"
                    continue
            elif is_list:
                html_parts[-1] += docx_parser.VListParagraph.type_to_html(list_type, False)
                is_list = False
            html_parts.append(part.to_html())
        if is_list:
            html_parts[-1] += docx_parser.VListParagraph.type_to_html(list_type, False)
        html_parts.append("[/hl]")
        return "\n".join(html_parts)

    def parse(self, cell: _Cell) -> []:
        for elem in cell._element:
            if type(elem) == CT_P:
                self.parts.append(docx_parser.VParagraph((Paragraph(elem, cell))))
            elif type(elem) == CT_Tbl:
                self.parts.extend(docx_parser.VTable(Table(elem, cell)).items)
        return self.parts
