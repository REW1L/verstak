import re


class Glue:
    NBSP = "&nbsp;"
    __nbsp_patterns = [
        {
            "nbsp_group": 2,
            "pattern": re.compile("(^|[0-9]+)([  ])°C", re.MULTILINE),
        },
        {
            "nbsp_group": 1,
            "pattern": re.compile('[А-ЯЁа-яё]([  ])(ли|ль|же|ж|бы|б)[^А-ЯЁа-яё]', re.MULTILINE),
        },
        {
            "nbsp_group": 2,
            "pattern": re.compile("(^|[^0-9—])[0-9,]+([  ])(тыс|млн|млрд|трлн)", re.MULTILINE),
        },
        {
            "nbsp_group": 2,
            "pattern": re.compile("(^|[^—0-9])[0-9][0-9][0-9,]+([  ])[A-Za-zА-Яа-я]+", re.MULTILINE),
        },
        {
            "nbsp_group": 3,
            "pattern": re.compile("(^|[^А-ЯЁа-яё—\\-]){}([  ]){}".format(
                "([Бб]ез|[Пп]ри|[Нн]ад|[Пп]од|[Пп]ро|[Дд]ля|[Уу]же)",
                "([A-Za-zА-Яа-я]+|[0-9]+)"),
                                  re.MULTILINE | re.IGNORECASE),
        },
        {
            "nbsp_group": 3,
            "pattern": re.compile("(^|[^А-ЯЁа-яё])([Тт]ак([  ])и|[Кк]ак([  ])и|[Вв]се([  ])равно|[Кк]роме([  ])того)"
                                  "[^А-ЯЁа-яё]",
                                  re.MULTILINE),
        },
    ]
    __nobr_patterns = [
        {
            "nobr_group": 2,
            "pattern": re.compile("(^|[^А-ЯЁа-яё])([A-Za-zА-Яа-я]+[  ]?-[  ]?(то|либо|нибудь|ка))([^А-ЯЁа-яё]|$)",
                                  re.MULTILINE),
        },
        {
            "nobr_group": 1,
            "pattern": re.compile("([0-9]+[0-9, ]*[  ]?— ?[0-9, ]*[0-9]+[  ]?"
                                  "([A-Za-zА-Яа-я/]+\\.?|[^,.;?'|`~! )(]+))",
                                  re.MULTILINE),
        },
        {
            "nobr_group": 2,
            "pattern": re.compile("(^|[^А-ЯЁа-яё])([иИ]з-за|[Вв]се-таки|т\\. ?д\\.|т\\. ?п\\.)", re.MULTILINE),
        },
        {
            "nobr_group": 2,
            "pattern": re.compile("(^|[^А-ЯЁа-яё])((По|В|Во|во|в|по)[  ]?-[  ]?[A-Za-zА-Яа-я]+)[^А-ЯЁа-яё]",
                                  re.MULTILINE),
        },
    ]

    __span_patterns = [
        {
            "span_group": 2,
            "pattern": re.compile(f'(^|[^А-ЯЁа-яё])([А-ЯЁа-яё]+({NBSP}|[  ])(ли|ль|же|ж|бы|б))([^А-ЯЁа-яё]|$)',
                                  re.MULTILINE),
        },
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
            founds = pattern['pattern'].finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(pattern['span_group']) >= 0:
                        span_indexes.append([search.start(pattern['span_group']),
                                             search.end(pattern['span_group'])])
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
            founds = pattern['pattern'].finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(pattern['nobr_group']) >= 0:
                        nobr_indexes.append([search.start(pattern['nobr_group']),
                                             search.end(pattern['nobr_group'])])
        return nobr_indexes

    @staticmethod
    def nbsp(sentence) -> list:
        """
        Get indexes for nbsp replacing in the text
        :param sentence: text to get indexes from
        :return: list of indexes where it needs to replace [index1, index2]
        """
        indexes = set()
        for pattern in Glue.__nbsp_patterns:
            founds = pattern['pattern'].finditer(sentence)
            if founds is not None:
                for search in founds:
                    if search.start(pattern['nbsp_group']) >= 0:
                        indexes.add(search.start(pattern['nbsp_group']))
        return list(indexes)


if __name__ == "__main__":
    from verstak_parser.VText import VText
    assert VText("678 678 фывфыв").do_typograf() == "678 678&nbsp;фывфыв"
    assert VText("678,67 млн долларов").do_typograf() == "678,67&nbsp;млн долларов"
    assert VText("про себя").do_typograf() == "про&nbsp;себя"
    assert VText("что-нибудь я сделаю").do_typograf() == "[nobr]что-нибудь[/nobr] я сделаю"
    assert VText("Как бы я хотел этого").do_typograf() == "<span>Как&nbsp;бы</span> я хотел этого"
    assert VText("1,5—2 часа").do_typograf() == "[nobr]1,5—2 часа[/nobr]"
    assert VText("много денег 12 009 — 17 877 ₽ или мало").do_typograf() == "много денег [nobr]12 009 — 17 877 ₽[/nobr]" \
                                                                            " или мало"
    assert VText("бла-бла, и т. д., и т.п.").do_typograf() == "бла-бла, и [nobr]т. д.[/nobr], и [nobr]т.п.[/nobr]"
    print("ALL IS OK")
