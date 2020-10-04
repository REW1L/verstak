import re


class Glue:
    NBSP = "&nbsp;"
    __nbsp_pre_patterns = [
        re.compile("([0-9]+)([  ])°C", re.MULTILINE),
        re.compile('([А-ЯЁа-яё])([  ])(ли|ль|же|ж|бы|б)[,;:?!"‘“» ]', re.MULTILINE),
        re.compile("(^|[^0-9—])[0-9,]+([  ])(тыс|млн|млрд|трлн)", re.MULTILINE),
    ]
    __nbsp_post_patterns = [
        re.compile("(^|[^—0-9])[0-9][0-9][0-9,]+([  ])[A-Za-zА-Яа-я]+", re.MULTILINE),
        re.compile("[^А-ЯЁа-яё—\\-]{}([  ]){}".format("([Бб]ез|[Пп]ри|[Нн]ад|[Пп]од|[Пп]ро|[Дд]ля|[Уу]же)",
                                                         "([A-Za-zА-Яа-я]+|[0-9]+)"),
                   re.MULTILINE | re.IGNORECASE),
        re.compile("([Тт]ак([  ])и|[Кк]ак([  ])и|[Вв]се([  ])равно|[Кк]роме([  ])того)[^А-ЯЁа-яё]",
                   re.MULTILINE),
    ]
    __nobr_patterns = [
        re.compile("[^А-ЯЁа-яё]([A-Za-zА-Яа-я]+[  ]?-[  ]?(то|либо|нибудь|ка))[^А-ЯЁа-яё]", re.MULTILINE),
        re.compile("([0-9]+[  ]?— ?[0-9]+[  ]?([A-Za-zА-Яа-я/]+\\.?|[^,.;?'|`~! )(]+))", re.MULTILINE),
        re.compile("([иИ]з-за|[Вв]се-таки|т\\. д\\.|т\\. п\\.)", re.MULTILINE),
        re.compile("[^А-ЯЁа-яё]((По|В|Во|во|в|по)[  ]?-[  ]?[A-Za-zА-Яа-я]+)[^А-ЯЁа-яё]", re.MULTILINE),
    ]

    __span_patterns = [
        re.compile(f'(^|[^А-ЯЁа-яё])([А-ЯЁа-яё]+({NBSP}|[  ])(ли|ль|же|ж|бы|б))([^А-ЯЁа-яё]|$)', re.MULTILINE),
    ]

    @staticmethod
    def span(sentence) -> list:
        """
        Get indexes for span wrapping in text
        :param sentence: text to get indexes from
        :return: list of indexes where it needs to wrap [[start, end], [start, end]]
        """
        span_indexes = []
        for pattern in Glue.__span_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(2) >= 0:
                        span_indexes.append([search.start(2), search.end(2)])
        return span_indexes

    @staticmethod
    def nobr(sentence) -> list:
        """
        Get indexes for nobr wrapping in text
        :param sentence: text to get indexes from
        :return: list of indexes where it needs to wrap [[start, end], [start, end]]
        """
        nobr_indexes = []
        for pattern in Glue.__nobr_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(1) >= 0:
                        nobr_indexes.append([search.start(1), search.end(1)])
        return nobr_indexes

    @staticmethod
    def __nbsp_pre(sentence: str) -> list:
        index_list = []
        for pattern in Glue.__nbsp_pre_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(1) >= 0:
                        index_list.append(search.start(2))
        return index_list

    @staticmethod
    def __nbsp_post(sentence) -> list:
        index_list = []
        for pattern in Glue.__nbsp_post_patterns:
            founds = pattern.finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(2) >= 0:
                        index_list.append(search.start(2))
        return index_list

    @staticmethod
    def nbsp(sentence) -> list:
        """
        Get indexes for nbsp replacing in the text
        :param sentence: text to get indexes from
        :return: list of indexes where it needs to replace [index1, index2]
        """
        indexes = set()
        indexes.update(Glue.__nbsp_pre(sentence))
        indexes.update(Glue.__nbsp_post(sentence))
        return list(indexes)


if __name__ == "__main__":
    indexes = Glue.nbsp("Мне показалось, что и сами шведы в целом такие — по-северному "
                        "простые и конкретные. Они достаточно закрытые и не очень общительные, но настолько воспитанные"
                        ", что при разговоре с другими стараются быть максимально дружелюбными — но, конечно, до"
                        " разумного предела. Еще они очень вежливы, и для них чуть ли не главное"
                        " — никак не задеть другого человека. Если им что-то не"
                        " понравится в вашем поведении, они никогда не скажут это в лицо — максимум напишут записку"
                        ", в которой объяснят, как и почему вы доставляете им неудобства. И даже эта записка все"
                        " равно будет очень вежливой — только если вы уж очень доведете шведа, он"
                        " наставит в записке восклицательных знаков.")
    from docx_parser.VText import VText
    print(VText("678 678 фывфыв").do_typograf())
    print(VText("678,67 млн долларов").do_typograf())

    print(indexes)
