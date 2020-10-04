from enum import Enum
from docx.table import Table, _Column

from .VPole import VPole
from .VPlashka import VPlashka
from .VBigTable import VBigTable
from .VText import VText


class VTable:
    class TYPE(Enum):
        """
        Type of VTable
        """
        NONE = 0
        POLES = 1
        PLASHKA = 2
        BIG_TABLE = 3

    def __init__(self, table: Table = None):
        """
        Table representation (Can be VPole/VPlashka/VBigTable)
        :param table: docx table to parse
        """
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
        """
        Get html representation
        :return: html representation
        """
        if self.type == VTable.TYPE.POLES or self.type == VTable.TYPE.PLASHKA:
            return "\n\n".join([x.to_html() for x in self])
        else:
            return "".join([x.to_html() for x in self])

    def do_typograf(self):
        """
        Rework text of parts by rules from typograph
        :return: resulted text
        """
        for item in self.items:
            item.do_typograf()

    def parse(self, table: Table) -> []:
        """
        Parse docx table
        :param table: docx table
        :return: list of included items in table (VPole/VPlashka/VBigTable)
        """
        rows_len = len(table.rows)
        columns_len = len(table.columns)
        if rows_len < 1:
            return []
        # 1. Pole should have 2 columns, right column thinner than 60% of the left column
        #    and text in the left part should be more than twice bigger than right part
        # 2. If table has only one cell in it then it is Plashka
        # 3. BigTable otherwise
        if columns_len == 2 and len(table.columns[0].cells) > 0 and len(table.columns[1].cells) > 0:
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
