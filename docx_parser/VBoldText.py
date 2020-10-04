from docx.oxml.text.run import CT_R

from .VText import VText


class VBoldText(VText):
    def __init__(self, bold_text: CT_R = None):
        """
        Class for bold text
        :param bold_text: CT_R part of docx paragraph with bold formatting
        """
        super(VBoldText, self).__init__()
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
        """
        Get html representation
        :return: html representation
        """
        if self.bold:
            warning = ""
            if self.glue_warning:
                warning = ' class="verstak_glue_warning"'
            return f"<strong{warning}>{self.text}</strong>"
        else:
            return self.text

    def parse(self, bold_text: CT_R):
        """
        Parse CT_R part of docx paragraph with bold formatting
        :param bold_text: CT_R part of docx paragraph with bold formatting
        :return: Markdown representation
        """
        self.text = bold_text.text
        self.raw = bold_text
        if bold_text.rPr.b is None:
            return f"{self.text}"
        if bold_text.text.strip() == "":
            return self.text
        self.bold = bold_text.rPr.b.val
        return str(self)
