import re


class Glue:
    NBSP = "\u00A0"
    __nbsp_pre_patterns = [
        re.compile("[^—0-9][0-9][0-9][0-9,]+( )[^ ]+", re.MULTILINE),
        re.compile("[0-9]+( )°C", re.MULTILINE),
        re.compile('[А-ЯЁа-яё]( )(ли|ль|же|ж|бы|б)[,;:?!"‘“» ]', re.MULTILINE),
        re.compile("[^0-9—][0-9]+( )?(тыс|млн|млрд|трлн)", re.MULTILINE)
    ]
    __nbsp_post_patterns = [
        re.compile("[^А-ЯЁа-яё—\\-]{}( ){}".format("(в|без|до|из|к|на|по|о|от|при|с|у|за|над|об|под|про|для)",
                                    "([A-Za-zА-Яа-я]+|[0-9]+)"),
                   re.MULTILINE | re.IGNORECASE),
        re.compile("(так( )и|как( )и|все( )равно|кроме( )того)[^А-ЯЁа-яё]", re.MULTILINE | re.IGNORECASE)
    ]
    __nobr_patterns = [
        re.compile("([A-Za-zА-Яа-я]+ ?- ?(то|либо|нибудь|ка))[^А-ЯЁа-яё]", re.MULTILINE),
        re.compile("([0-9]+ ?— ?[0-9]+ ?([A-Za-zА-Яа-я]+\\.?|[^,.;/?'|`~!]+))", re.MULTILINE),
    ]

    __span_patterns = [
        re.compile('[^А-ЯЁа-яё]([А-ЯЁа-яё]+[ \u00A0](ли|ль|же|ж|бы|б))[^А-ЯЁа-яё]', re.MULTILINE),
    ]

    @staticmethod
    def span(sentence):
        span_indexes = []
        for pattern in Glue.__span_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    span_indexes.append([search.start(1), search.end(1)])
        return span_indexes

    @staticmethod
    def nobr(sentence) -> list:
        nobr_indexes = []
        for pattern in Glue.__nobr_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    nobr_indexes.append([search.start(1), search.end(1)])
        return nobr_indexes

    @staticmethod
    def __nbsp_pre(sentence: str) -> list:
        index_list = []
        for pattern in Glue.__nbsp_pre_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    index_list.append(search.start(1))
        return index_list

    @staticmethod
    def __nbps_post(sentence) -> list:
        index_list = []
        for pattern in Glue.__nbsp_post_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    index_list.append(search.start(2))
        return index_list

    @staticmethod
    def nbsp(sentence) -> list:
        indexes = Glue.__nbsp_pre(sentence)
        indexes.extend(Glue.__nbps_post(sentence))
        return indexes
