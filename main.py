import os
from docx_parser import VDocument


def main():
    docs = os.listdir("docs")
    i = 1
    for doc in docs:
        if not doc.startswith(".") and not doc.startswith("~"):
            print(f"Started parsing  ({i}/{len(docs)}): {doc}")
            document = VDocument.from_file(f"docs{os.sep}{doc}")
            document.store_markdown(f"markdown{os.sep}{doc}.md")
            document.store_html(f"html{os.sep}{doc}.html")
            print(f"Finished parsing ({i}/{len(docs)}): {doc}")
        i += 1
    print("Done")


if __name__ == "__main__":
    main()
