from docx.oxml.text.run import CT_R


class VPicture:
    def __init__(self, raw: CT_R = None):
        self.caption = []
        self.raw = raw

    @property
    def text(self):
        return str(self)

    def __str__(self):
        caption = "".join([str(x) for x in self.caption])
        caption = caption.replace("\n", "")
        return f'[img src="placeholder1400" prop="" caption="{caption}"]'

    def to_html(self):
        caption = "".join([x.to_html() for x in self.caption if type(x) != str])
        caption = caption.replace("\n", "")
        return f'[img src="placeholder1400" prop="" caption="{caption}"]'

    def parse(self, caption: str = "") -> str:
        self.caption = caption
        return str(self)

    def do_typograf(self):
        pass
