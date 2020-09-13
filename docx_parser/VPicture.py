from docx.oxml.text.run import CT_R


class VPicture:
    def __init__(self, raw: CT_R = None):
        self.caption = ""
        self.raw = raw

    def __str__(self):
        return f'\n[img src="placeholder1400" prop="" caption="{self.caption}"]'

    def to_html(self):
        return str(self)

    def parse(self, caption: str = "") -> str:
        self.caption = caption
        return str(self)
