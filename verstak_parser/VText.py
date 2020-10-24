from .typograf import Glue


class VText:
    def __init__(self, text: str = ""):
        """
        Common class for text object from docx
        :param text: text of element
        """
        self.text = text
        self.glue_warning = False
        self.glue = Glue()

    def __str__(self):
        return self.text

    def to_html(self) -> str:
        """
        Get html representation
        :return: html representation
        """
        return self.text

    def add_glue(self, nobr_start: int, nobr_end: int, glue_type: str = "nobr") -> int:
        """
        Connect parts of text with special tag (e.g. [nobr][/nobr])
        :param nobr_start: start index of gluing sentence
        :param nobr_end: end index of gluing sentence
        :param glue_type: type of glue tag (nobr/span)
        :return: amount of characters on which text was extended
        """
        text = self.text
        if glue_type == "nobr":
            open_tag = f"[{glue_type}]"
            close_tag = f"[/{glue_type}]"
        elif glue_type == "span":
            open_tag = f"<{glue_type}>"
            close_tag = f"</{glue_type}>"
        else:
            raise Exception(f"Glue type ({glue_type}) is not known")
        self.text = "{}{}{}{}{}".format(text[:nobr_start], open_tag,
                                        text[nobr_start:nobr_end],
                                        close_tag, text[nobr_end:])
        return len(open_tag) + len(close_tag)

    def replace_char_in_place(self, index: int, char: str) -> int:
        """
        Replace char in text object
        :param index: index of char to replace
        :param char: char/string to use for replacing
        :return: difference in length of the previous text and the result
        """
        text = self.text
        previous_len = len(text)
        if len(self.text) > index + 1:
            self.text = f"{text[:index]}{char}{text[index+1:]}"
        else:
            self.text = f"{text[:index]}{char}"
        return len(self.text) - previous_len

    def __add_nobr(self):
        """
        Add nobr by rules from typograph
        """
        nobr_indexes = self.glue.nobr(self.text)
        nobr_indexes.sort()
        if len(nobr_indexes) > 0:
            shift = 0
            for index in nobr_indexes:
                shift += self.add_glue(index[0] + shift, index[1] + shift)

    def __add_nbsp(self):
        """
        Add nbsp by rules from typograph
        """
        nbsp_indexes = self.glue.nbsp(self.text)
        if len(nbsp_indexes) > 0:
            nbsp_indexes.sort()
            shift = 0
            for index in nbsp_indexes:
                shift += self.replace_char_in_place(index + shift, self.glue.NBSP)

    def __add_span(self):
        """
        Add span by rules from typograph
        """
        span_indexes = self.glue.span(self.text)
        if len(span_indexes) > 0:
            span_indexes.sort()
            shift = 0
            for index in span_indexes:
                shift += self.add_glue(index[0] + shift, index[1] + shift, "span")

    def do_typograf(self, nobr_enabled: bool = True):
        """
        Rework text by rules from typograph
        :param nobr_enabled: allow nobr additions
        :return: resulted text
        """
        if nobr_enabled:
            self.__add_nobr()
        self.__add_nbsp()
        self.__add_span()
        return self.text
