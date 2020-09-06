from docx.table import Table


class VBigTable:
    def __init__(self, table: Table = None, title: str = ""):
        self.title = title
        self.raw = table

    def __str__(self):
        return "## BIG TABLE"
