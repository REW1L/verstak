from docx.oxml.text.run import CT_R


class VPicture:
    def __init__(self, raw: CT_R = None):
        """
        Class for pictures in text
        :param raw: CT_R with picture
        """
        self.caption = []
        self.raw = raw

    @property
    def text(self):
        """
        Text representation of picture
        :return: text representation of picture
        """
        return str(self)

    def __str__(self):
        caption = "".join([str(x) for x in self.caption])
        caption = caption.replace("\n", "")
        return f'[img src="placeholder1400" prop="" caption="{caption}"]'

    def to_html(self):
        """
        Get html representation
        :return: html representation
        """
        caption = "".join([x.to_html() for x in self.caption if type(x) != str])
        caption = caption.replace("\n", "")
        return f'[img src="placeholder1400" prop="" caption="{caption}"]'

    def parse(self, caption: str = "") -> str:
        """
        Parse picture
        :param caption: caption of the picture to be set
        :return: text representation of picture
        """
        self.caption = caption
        return str(self)

    def do_typograf(self):
        pass
