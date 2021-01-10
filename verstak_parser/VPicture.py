from docx.oxml.text.run import CT_R
from .VText import VText


class VTextPicture(VText):

    def __init__(self, text=""):
        """
        Class for text in captions with special nobr rules
        :param text: text in a part
        """
        super(VTextPicture, self).__init__(text)

    def do_typograf(self, nobr_enabled: bool = True):
        """
        Rework text by rules from typograph
        :param nobr_enabled: allow nobr additions
        :return: resulted text
        """
        super(VTextPicture, self).do_typograf(nobr_enabled)
        self.text = self.text.replace("[nobr]", "<nobr>")
        self.text = self.text.replace("[/nobr]", "</nobr>")


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

    def do_typograf(self, nobr_enabled: bool = True):
        """
        Rework text from caption by rules from typograph
        :return: text representation of picture
        """
        for index in range(len(self.caption)):
            if type(self.caption[index]) == str:
                part = VText(self.caption[index])
            else:
                part = self.caption[index]
            new_part = VTextPicture(part.text)
            new_part.do_typograf(nobr_enabled)
            part.text = new_part.text
            self.caption[index] = part
        return self.text
