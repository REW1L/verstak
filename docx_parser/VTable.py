from enum import Enum
from docx.table import Table, _Column

from .VPole import VPole
from .VPlashka import VPlashka
from .VBigTable import VBigTable
from .VText import VText


class VTable:
    class TYPE(Enum):
        NONE = 0
        POLES = 1
        PLASHKA = 2
        BIG_TABLE = 3

    def __init__(self, table: Table = None):
        self.raw = table
        self.type = VTable.TYPE.NONE
        self.items = []
        if table is not None:
            self.parse(table)

    def __iter__(self):
        return self.items.__iter__()

    def __str__(self):
        return "".join([str(x) for x in self])

    def to_html(self):
        if self.type == VTable.TYPE.POLES or self.type == VTable.TYPE.PLASHKA:
            return "\n\n".join([x.to_html() for x in self])
        else:
            return "".join([x.to_html() for x in self])

    def do_typograf(self):
        for item in self.items:
            item.do_typograf()

    def parse(self, table: Table) -> []:
        rows_len = len(table.rows)
        columns_len = len(table.columns)
        if rows_len < 1:
            return []
        if columns_len == 2:
            left_column: _Column = table.columns[0]
            right_column: _Column = table.columns[1]
            if float(left_column._gridCol.values()[0]) * 0.6 > float(right_column._gridCol.values()[0]) and \
               len(left_column.cells[0].text) * 0.5 > len(right_column.cells[0].text):
                self.items.extend(VPole.parse_poles(table))
                self.type = VTable.TYPE.POLES
            else:
                self.type = VTable.TYPE.BIG_TABLE
                self.items.append(VBigTable(table))
        elif columns_len == 1:
            self.items.append(VPlashka(table.rows[0].cells[0]))
            self.type = VTable.TYPE.PLASHKA
        else:
            self.type = VTable.TYPE.BIG_TABLE
            self.items.append(VBigTable(table))
        if rows_len > 1 and columns_len == 1:
            rows = table.rows[1:]
            for row in rows:
                for cell in row.cells:
                    self.items.append(VText(cell.text))
        return self.items
