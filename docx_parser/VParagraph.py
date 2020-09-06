import re
from typing import Union
from docx.oxml.text.run import CT_R
from docx.oxml.text.font import CT_RPr
from docx.oxml.text.parfmt import CT_PPr
from docx.text.paragraph import Paragraph

from .VPicture import VPicture
from .VHyperlink import VHyperlink
from .VBoldText import VBoldText
from .VText import VText
from .VListParagraph import VListParagraph


class VParagraph:
    def __init__(self, paragraph: Paragraph = None, title: bool = True):
        self.parts = []
        self.raw: Paragraph = paragraph
        self.title_enabled = title
        self.title = False
        self.title_level = 0
        if paragraph is not None:
            self.parse(paragraph, title)

    def __len__(self):
        return len(self.parts)

    def __str__(self):
        if self.title:
            parts = [f'#{"#" * self.title_level} ']
            parts.extend(self.parts)
        else:
            parts = self.parts
        return "".join([str(x) for x in parts])

    def __getitem__(self, item):
        return self.parts[item]

    def __setitem__(self, key, value):
        self.parts[key] = value

    def __iter__(self):
        return self.parts.__iter__()

    def is_picture(self) -> bool:
        for part in self.parts:
            if type(part) == VPicture:
                return True
        return False

    def __parse_title(self):
        if not self.title_enabled:
            return
        if self.raw.style.name.lower().startswith("title"):
            self.title = True
            self.title_level = 0
        elif self.raw.style.name.lower().startswith("heading "):
            self.title = True
            heading_regexp = re.search("heading ([0-9]+)", self.raw.style.name.lower())
            if heading_regexp is not None and len(heading_regexp.groups()) > 0:
                self.title_level = int(heading_regexp.group(1))

    def __merge_last_hyperlinks(self, hyperlink: VHyperlink) -> bool:
        if len(self.parts) > 0 and type(self.parts[-1]) == VHyperlink:
            if hyperlink.text.startswith(self.parts[-1].text):
                self.parts[-1] = hyperlink
            elif hyperlink.url == self.parts[-1].url:
                self.parts[-1].text = f"{self.parts[-1].text}{hyperlink.text}"
            else:
                return False
        else:
            return False
        return True

    def __parse_run(self, run: CT_R) -> Union[VBoldText, VPicture, VText, None]:
        part = None
        if type(run[0]) == CT_RPr:
            if run[0].b is not None:
                part = VBoldText(run)
                if self.__merge_last_bold_text(part):
                    return None
            elif len([tag for tag in run if tag.tag.endswith("drawing")]) > 0:
                part = VPicture(run)
            else:
                part = VText(run.text)
        elif len([x for x in run if x.tag.endswith("drawing")]) > 0:
            part = VPicture(run)
        return part

    def __merge_last_bold_text(self, bold_text: VBoldText) -> bool:
        if len(self.parts) > 0 and type(self.parts[-1]) == VBoldText:
            self.parts[-1].text += bold_text.text
            return True
        return False

    def __move_text_to_caption(self):
        caption = ""
        new_parts = []
        img = None
        for part in self.parts:
            if type(part) != VPicture:
                caption += str(part)
            else:
                if img is None:
                    img = part
                new_parts.append(part)
        if img is not None and caption != "":
            new_parts[0].caption = caption
            self.parts = new_parts

    def parse(self, paragraph: Paragraph, title: bool = True) -> str:
        self.raw = paragraph
        self.title_enabled = title
        self.__parse_title()
        for elem in paragraph._element:
            part = None
            if elem.tag.endswith("hyperlink"):
                part = VHyperlink(elem, paragraph)
                if self.__merge_last_hyperlinks(part):
                    continue
            elif type(elem) == CT_PPr:
                if elem.numPr is not None:
                    part = VListParagraph(elem, paragraph)
            elif type(elem) == CT_R:
                part = self.__parse_run(elem)
            else:
                if elem.text is not None:
                    part = VText(elem.text)
            if part is not None:
                self.parts.append(part)
        if self.is_picture():
            self.__move_text_to_caption()
        return str(self)