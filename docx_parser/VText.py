from .typograf import Glue


class VText:
    def __init__(self, text: str = ""):
        self.text = text
        self.glue_warning = False

    def __str__(self):
        return self.text

    def to_html(self):
        return self.text

    def add_glue(self, nobr_start: int, nobr_end: int, glue_type: str = "nobr"):
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

    def replace_char_in_place(self, index: int, char: str):
        text = self.text
        previous_len = len(text)
        if len(self.text) > index + 1:
            self.text = f"{text[:index]}{char}{text[index+1:]}"
        else:
            self.text = f"{text[:index]}{char}"
        return len(self.text) - previous_len

    def __add_nobr(self):
        nobr_indexes = Glue.nobr(self.text)
        nobr_indexes.sort()
        if len(nobr_indexes) > 0:
            shift = 0
            for index in nobr_indexes:
                shift += self.add_glue(index[0] + shift, index[1] + shift)

    def __add_nbsp(self):
        nbsp_indexes = Glue.nbsp(self.text)
        if len(nbsp_indexes) > 0:
            nbsp_indexes.sort()
            shift = 0
            for index in nbsp_indexes:
                shift += self.replace_char_in_place(index + shift, Glue.NBSP)

    def __add_span(self):
        span_indexes = Glue.span(self.text)
        if len(span_indexes) > 0:
            span_indexes.sort()
            shift = 0
            for index in span_indexes:
                shift += self.add_glue(index[0] + shift, index[1] + shift, "span")

    def do_typograf(self, nobr_enabled: bool = True):
        if nobr_enabled:
            self.__add_nobr()
        self.__add_nbsp()
        self.__add_span()
