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

    def parse(self, cell: _Cell) -> []:
        for elem in cell._element:
            if type(elem) == CT_P:
                self.parts.append(docx_parser.VParagraph((Paragraph(elem, cell))))
            elif type(elem) == CT_Tbl:
                self.parts.extend(docx_parser.VTable(Table(elem, cell)).items)
        return self.parts
