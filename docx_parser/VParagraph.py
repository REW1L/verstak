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
from .typograf import Glue


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
            parts.extend([x.text for x in self.parts])
            return "".join(parts)
        else:
            parts = self.parts
        return "".join([str(x) for x in parts])

    def __getitem__(self, item):
        return self.parts[item]

    def __setitem__(self, key, value):
        self.parts[key] = value

    def __iter__(self):
        return self.parts.__iter__()

    def to_html(self, is_warning: bool = False, allow_header_links: bool = False):
        html_list = []
        if str(self) == "":
            return ""
        text_length = len(self.text)
        if self.title and text_length < 90:
            html_list.append(VText(f"<h2>"))
        elif self.title and text_length >= 90:
            html_list.append(VText(f'<p class="verstak_warning">'))
        elif self.list_type is None and not self.is_picture():
            if is_warning:
                html_list.append(VText(f'<p class="verstak_warning">'))
            else:
                html_list.append(VText("<p>"))

        for part in self.parts:
            if self.title and allow_header_links:
                if type(part) != VHyperlink:
                    part = VText(part.text)
            html_list.append(part)

        if self.title and text_length < 90:
            html_list.append(VText(f"</h2>"))
        elif self.title and text_length >= 90:
            html_list.append(VText(f"</p>"))
        elif self.list_type is None and not self.is_picture():
            html_list.append(VText(f"</p>"))

        if self.title and not is_warning and not allow_header_links:
            return "".join([x.text for x in html_list])
        elif self.is_picture():
            html_str = html_list[0].to_html()
            for part in html_list[1:]:
                if type(part) == VPicture:
                    html_list += "\n"
                html_list += part.to_html()
            return html_str
        else:
            return "".join([x.to_html() for x in html_list]).replace("\n", "")

    def __enlarge_parts(self):
        if self.is_picture():
            return
        for index in range(1, len(self.parts)):
            if type(self[index]) == VHyperlink:
                continue
            if type(self[index]) == type(self[index-1]):
                alt_part_index = index
                break
            elif self[index].text.strip() == "" and type(self[index-1]) != VHyperlink:
                alt_part_index = index
                break
        else:
            return
        head = self.parts[:alt_part_index]
        head[-1].text = self[alt_part_index-1].text + self[alt_part_index].text
        if len(self.parts) > alt_part_index:
            head.extend(self.parts[alt_part_index+1:])
        self.parts = head
        self.__enlarge_parts()

    def do_typograf(self, nobr_enabled: bool = True):
        if self.is_picture() or self.text.strip() == "":
            return
        for part in self:
            if type(part) != VListParagraph:
                part.do_typograf(nobr_enabled)

    def is_picture(self) -> bool:
        for part in self.parts:
            if type(part) == VPicture:
                return True
        return False

    def get_links_indexes(self):
        indexes = []
        for index in range(len(self)):
            if type(self[index]) == VHyperlink:
                indexes.append(index)
        return indexes

    @property
    def list_type(self):
        for part in self.parts:
            if type(part) == VListParagraph:
                return part.type
        return None

    @property
    def text(self):
        text = ""
        for part in self.parts:
            text.replace("\n", "")
            text += part.text
        return text

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
                if part.bold:
                    if self.__merge_last_bold_text(part):
                        return None
                else:
                    part = VText(part.text)
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
        caption = []
        new_parts = []
        img = None
        for part in self.parts:
            if type(part) != VPicture:
                caption.append(part)
            else:
                if img is None:
                    img = part
                new_parts.append(part)
        if img is not None and "".join(str(x) for x in caption) != "":
            new_parts[0].caption = caption
            self.parts = new_parts

    def find_new_lines(self):
        split_index = -1
        for index in range(len(self.parts)):
            if self.parts[index].text.find("\n") != -1:
                split_index = index
                break
        return split_index

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
        self.__enlarge_parts()
        return str(self)
