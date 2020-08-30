import os
import re
import json
import docx
from lxml.etree import _Element
from docx.document import Document
from docx.oxml.text.run import CT_R
from docx.oxml.text.font import CT_RPr
from docx.oxml.text.parfmt import CT_PPr
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.oxml.numbering import CT_NumPr
from docx.text.paragraph import Paragraph
from docx.table import Table, _Row, _Cell
from docx.opc.rel import _Relationship


def parse_hyperlink(hyperlink: _Element, paragraph: Paragraph) -> str:
    url_id = None
    if len(hyperlink.values()) > 0:
        url_id = hyperlink.values()[0]
    url: _Relationship = paragraph.part.rels[url_id]
    url = url.target_ref
    text = hyperlink[0].text
    return f"[{text}]({url})"


def parse_bold(bold_text: CT_R) -> str:
    if bold_text.rPr.b is None:
        return f"{bold_text.text}"
    if bold_text.text.strip() == "":
        return ""
    bold_enabled = bold_text.rPr.b.val
    if bold_enabled:
        return f"**{bold_text.text.strip()}** "
    else:
        return f"{bold_text.text}"


def parse_list(list_text: CT_PPr) -> str:
    option: CT_NumPr = list_text.numPr
    text = "  " * option.ilvl.val
    if option.numId.val < 3:
        text += "- "
    else:
        text += "1. "
    return text


def mock_picture() -> str:
    return '\n[img src="" prop="" caption=""]\n'


def parse_run(run: CT_R) -> str:
    line = ""
    if type(run[0]) == CT_RPr:
        if run[0].b is not None:
            line = parse_bold(run)
        elif len([tag for tag in run if tag.tag.endswith("drawing")]) > 0:
            line = mock_picture()
        else:
            line = run.text
    elif len([x for x in run if x.tag.endswith("drawing")]) > 0:
        line = mock_picture()
    return line


def parse_title(paragraph: Paragraph) -> list:
    text = []
    if paragraph.style.name.lower().startswith("title"):
        text.append("# ")
    elif paragraph.style.name.lower().startswith("heading "):
        heading_regexp = re.search("heading ([0-9]+)", paragraph.style.name.lower())
        if heading_regexp is not None and len(heading_regexp.groups()) > 0:
            heading_level = "#" * int(heading_regexp.group(1))
            text.append(f"#{heading_level} ")
    return text


def parse_paragraph(paragraph: Paragraph) -> str:
    text = []
    text.extend(parse_title(paragraph))
    for elem in paragraph._element:
        line = ""
        if elem.tag.endswith("hyperlink"):
            line = parse_hyperlink(elem, paragraph)
        elif type(elem) == CT_PPr:
            if elem.numPr is not None:
                line = parse_list(elem)
        elif type(elem) == CT_R:
            line = parse_run(elem)
            if len(text) > 0 and line.startswith("**") and text[-1].endswith("** "):
                line = line[2:]
                text[-1] = text[-1][:-3]
        else:
            if elem.text is not None:
                line = elem.text
        if line != "":
            text.append(line)
    return "".join(text)


def parse_pole(table: Table) -> list:
    section = []
    pole = {}
    row: _Row = table.rows[0]
    left: _Cell = row.cells[0]
    right: _Cell = row.cells[1]
    pole["left"] = []
    pole["right"] = []
    section.append("```json")
    for para in left.paragraphs:
        pole["left"].append(parse_paragraph(para))
    for para in right.paragraphs:
        pole["right"].append(parse_paragraph(para))
    if len(pole["right"]) == 1:
        url_regexp = re.search("^\[.*\]\((.*)\)$", pole["right"][0])
        if url_regexp is not None and len(url_regexp.groups()) == 1:
            pole["url"] = url_regexp.group(1)
    for line in json.dumps(pole, sort_keys=False, indent=2, ensure_ascii=False).splitlines():
        section.append(line)
    section.append("```")
    return section


def parse_plashka(cell: _Cell) -> list:
    plashka = list()
    plashka.append("```plashka")
    for paragraph in cell.paragraphs:
        plashka.append(parse_paragraph(paragraph))
    plashka.append("```")
    return plashka


def parse_table(table: Table) -> list:
    section = []
    rows_len = len(table.rows)
    columns_len = len(table.columns)
    if rows_len < 1:
        return []
    if rows_len >= 1:
        if columns_len == 2:
            section.extend(parse_pole(table))
        elif columns_len == 1:
            section.extend(parse_plashka(table.rows[0].cells[0]))
    if rows_len > 1 and columns_len > 1:
        return ["## BIG TABLE"]
    if rows_len > 1:
        rows = table.rows[1:]
        for row in rows:
            for cell in row.cells:
                section.append(cell.text)
    return section


def parse_document(document: Document):
    first_table_found = False
    text = []
    for elem in document.element.body:
        if type(elem) == CT_P:
            text.append(parse_paragraph(Paragraph(elem, document)))
        elif type(elem) == CT_Tbl:
            if not first_table_found:
                first_table_found = True
                continue
            text.extend(parse_table(Table(elem, document)))
    return text


def parse_doc_file(doc_path: str) -> list:
    document: Document = docx.Document(doc_path)
    return parse_document(document)


def store_markdown(lines: list, path: str = f"markdown{os.sep}result.md"):
    with open(path, "w") as result_file:
        for line in lines:
            result_file.write(f"{line}\n")
        result_file.flush()


def main():
    for doc in os.listdir("docs"):
        if not doc.startswith(".") and not doc.startswith("~"):
            lines = parse_doc_file(f"docs{os.sep}{doc}")
            store_markdown(lines, f"markdown{os.sep}{doc}.md")


if __name__ == "__main__":
    main()
