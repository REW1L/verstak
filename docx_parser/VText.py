class VText:
    def __init__(self, text: str = ""):
        self.text = text

    def __str__(self):
        return self.text

    def to_html(self):
        return self.text
