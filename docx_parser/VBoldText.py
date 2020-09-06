from docx.oxml.text.run import CT_R


class VBoldText:
    def __init__(self, bold_text: CT_R = None):
        self.text = ""
        if bold_text is not None:
            self.parse(bold_text)
        else:
            self.raw = bold_text

    def __str__(self):
        return f"**{self.text}**"

    def parse(self, bold_text: CT_R):
        self.text = bold_text.text
        self.raw = bold_text
        if bold_text.rPr.b is None:
            return f"{self.text}"
        if bold_text.text.strip() == "":
            return self.text
        bold_enabled = bold_text.rPr.b.val
        if bold_enabled:
            return str(self)
        else:
            return f"{self.text}"
