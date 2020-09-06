import json
from docx.table import Table, _Row, _Cell

from .VParagraph import VParagraph
from .VHyperlink import VHyperlink


class VPole:
    def __init__(self, row: _Row = None):
        self.title = ""
        self.left_parts = []
        self.right_parts = []
        self.url = ""
        self.raw = row
        if row is not None:
            self.parse(row)

    def __dict__(self):
        d = {
            "left": [str(x) for x in self.left_parts],
            "right": [str(x) for x in self.right_parts]
        }
        if self.url != "":
            d["url"] = self.url
        return d

    def __str__(self):
        section = ["```json"]
        for line in json.dumps(self.__dict__(),
                               sort_keys=False,
                               indent=2,
                               ensure_ascii=False).splitlines():
            section.append(line)
        section.append("```")
        return "\n".join(section)

    def parse(self, row: _Row):
        left: _Cell = row.cells[0]
        right: _Cell = row.cells[1]
        self.left_parts = []
        self.right_parts = []
        for para in left.paragraphs:
            paragraph = VParagraph(para, False)
            if str(paragraph).strip() != "":
                self.left_parts.append(paragraph)
        for para in right.paragraphs:
            paragraph = VParagraph(para, False)
            if str(paragraph).strip() != "":
                self.right_parts.append(paragraph)
        if len(self.right_parts) == 1:
            right_paragraph_part: VHyperlink = self.right_parts[0][0]
            if type(right_paragraph_part) == VHyperlink:
                self.url = right_paragraph_part.url
                self.right_parts = [right_paragraph_part.text]

    @staticmethod
    def parse_poles(table: Table) -> list:
        poles = []
        for row in table.rows:
            poles.append(VPole(row))
        return poles
