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

    def replace_char_in_place(self, index: int, char: str):
        text = self.text
        if len(self.text) > index + 1:
            self.text = f"{text[:index]}{char}{text[index+1:]}"
        else:
            self.text = f"{text[:index]}{char}"

    def do_typograf(self, nobr_enabled: bool = True):
        if nobr_enabled:
            nobr_indexes = Glue.nobr(self.text)
            if len(nobr_indexes) > 0:
                for index in nobr_indexes:
                    self.add_glue(index[0], index[1])
        nbsp_indexes = Glue.nbsp(self.text)
        if len(nbsp_indexes) > 0:
            for index in nbsp_indexes:
                self.replace_char_in_place(index, Glue.NBSP)
        span_indexes = Glue.span(self.text)
        if len(span_indexes) > 0:
            for index in span_indexes:
                self.add_glue(index[0], index[1], "span")
