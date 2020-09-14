from docx.oxml.text.run import CT_R


class VBoldText:
    def __init__(self, bold_text: CT_R = None):
        self.text = ""
        self.bold = False
        if bold_text is not None:
            self.parse(bold_text)
        else:
            self.raw = bold_text

    def __str__(self):
        if self.bold:
            return f"**{self.text}**"
        else:
            return self.text

    def to_html(self):
        if self.bold:
            return f"<strong>{self.text}</strong>"
        else:
            return self.text

    def parse(self, bold_text: CT_R):
        self.text = bold_text.text
        self.raw = bold_text
        if bold_text.rPr.b is None:
            return f"{self.text}"
        if bold_text.text.strip() == "":
            return self.text
        self.bold = bold_text.rPr.b.val
        return str(self)
