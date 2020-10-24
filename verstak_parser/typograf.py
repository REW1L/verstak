import re
import configparser
import os

config_dir = os.path.dirname(os.path.realpath(__file__))
configs = [f"{config_dir}{os.sep}default_tipograf.ini"]
if os.getenv("VERSTAK_CONFIG") is not None:
    configs.append(os.getenv("VERSTAK_CONFIG"))
config = configparser.ConfigParser()
config.read(configs)


class Glue:
    def __init__(self):
        self.__span_patterns = []
        self.__nbsp_patterns = []
        self.__nobr_patterns = []
        self.__configs = configs
        self.NBSP = config["DEFAULT"]["NBSP"]
        for key in config:
            if key == "DEFAULT":
                continue
            if "pattern" not in config[key] or "group" not in config[key]:
                print(f"WARNING: Section {key} in configure file has wrong format, "
                      f"continuing without it")
                continue
            pattern = {
                "group": int(config[key]['group']),
                "pattern": re.compile(config[key]['pattern'].strip().format(NBSP=self.NBSP),
                                      re.MULTILINE | re.IGNORECASE)
            }
            if key.startswith("SPAN"):
                self.__span_patterns.append(pattern)
            elif key.startswith("NBSP"):
                self.__nbsp_patterns.append(pattern)
            elif key.startswith("NOBR"):
                self.__nobr_patterns.append(pattern)
            else:
                print(f"WARNING: Section {key} in configure file has wrong format, "
                      f"continuing without it")

    def configs_paths(self):
        return self.__configs

    def span(self, sentence) -> list:
        """
        Get indexes for span wrapping in text
        :param sentence: text to get indexes from
        :return: list of indexes where it needs to wrap [[start, end], [start, end]]
        """
        span_indexes = []
        for pattern in self.__span_patterns:
            founds = pattern['pattern'].finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(pattern['group']) >= 0:
                        span_indexes.append([search.start(pattern['group']),
                                             search.end(pattern['group'])])
        return span_indexes

    def nobr(self, sentence) -> list:
        """
        Get indexes for nobr wrapping in text
        :param sentence: text to get indexes from
        :return: list of indexes where it needs to wrap [[start, end], [start, end]]
        """
        nobr_indexes = []
        for pattern in self.__nobr_patterns:
            founds = pattern['pattern'].finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(pattern['group']) >= 0:
                        nobr_indexes.append([search.start(pattern['group']),
                                             search.end(pattern['group'])])
        return nobr_indexes

    def nbsp(self, sentence) -> list:
        """
        Get indexes for nbsp replacing in the text
        :param sentence: text to get indexes from
        :return: list of indexes where it needs to replace [index1, index2]
        """
        indexes = set()
        for pattern in self.__nbsp_patterns:
            founds = pattern['pattern'].finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(pattern['group']) >= 0:
                        indexes.add(search.start(pattern['group']))
        return list(indexes)


if __name__ == "__main__":
    from verstak_parser.VText import VText
    assert VText("678 678 фывфыв").do_typograf() == "678 678&nbsp;фывфыв", \
        VText("678 678 фывфыв").do_typograf()
    assert VText("678,67 млн долларов").do_typograf() == "678,67&nbsp;млн долларов", \
        VText("678,67 млн долларов").do_typograf()
    assert VText("про себя").do_typograf() == "про&nbsp;себя", \
        VText("про себя").do_typograf()
    assert VText("что-нибудь я сделаю").do_typograf() == "[nobr]что-нибудь[/nobr] я сделаю", \
        VText("что-нибудь я сделаю").do_typograf()
    assert VText("Как бы я хотел этого").do_typograf() == "<span>Как&nbsp;бы</span> я хотел этого", \
        VText("Как бы я хотел этого").do_typograf()
    assert VText("1,5—2 часа").do_typograf() == "[nobr]1,5—2 часа[/nobr]", \
        VText("1,5—2 часа").do_typograf()
    assert VText("много денег 12 009 — 17 877 ₽ или мало").do_typograf() == "много денег [nobr]12 009 — 17 877 ₽[/nobr]" \
                                                                            " или мало", \
        VText("много денег 12 009 — 17 877 ₽ или мало").do_typograf()
    assert VText("бла-бла, и т. д., и т.п.").do_typograf() == "бла-бла, и [nobr]т. д.[/nobr], и [nobr]т.п.[/nobr]", \
        VText("бла-бла, и т. д., и т.п.").do_typograf()
    assert VText("для себя").do_typograf() == "для&nbsp;себя", \
        VText("для себя").do_typograf()
    assert VText("текст 110, если текст").do_typograf() == "текст 110, если текст", \
        VText("текст 110, если текст").do_typograf()
    assert VText("20:00, но").do_typograf() == "20:00, но", \
        VText("20:00, но").do_typograf()
    assert VText("из-за кота не получилось уснуть").do_typograf() == "[nobr]из-за кота[/nobr] не получилось уснуть", \
        VText("все-таки мне из-за кота не получилось уснуть").do_typograf()
    assert VText("все-таки мне получилось уснуть").do_typograf() == "[nobr]все-таки[/nobr] мне получилось уснуть", \
        VText("все-таки мне получилось уснуть").do_typograf()
    print("ALL IS OK")
