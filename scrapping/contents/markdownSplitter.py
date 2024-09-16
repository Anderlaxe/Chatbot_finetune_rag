import pandoc
from pandoc.types import *
import os, json

def markdown_splitter(markdown: str):
    content = pandoc.read(markdown, format="markdown")

    headings = [None, None, None, None]
    bag = []
    contents = []

    for elt in content[1]:
        if isinstance(elt, Header):
            level = elt[0]-1
            if level < len(headings):
                if all([x is None for x in headings]):
                    headings[level] = elt
                    bag = []
                else:
                    part = [h for h in headings[:] if h is not None]
                    for smthg in bag:
                        part.append(smthg)
                    bag = []
                    contents.append(part)

                    headings[level] = elt
                    for i in range(level+1, len(headings)):
                        headings[i] = None
            else:
                bag.append(elt)
        else:
            bag.append(elt)
    
    part = [h for h in headings[:] if h is not None]
    for smthg in bag:
        part.append(smthg)
    bag = []
    contents.append(part)

    results = []

    for elt in contents:
        doc = Pandoc(Meta({}), elt)
        string = pandoc.write(doc, format="markdown", options=["--wrap=none"])
        results.append(string)
    return results


RAW_FOLDER = "./raw/"
PAGES_FOLDER = "./pages/"

database = []

with open(RAW_FOLDER + "@sources.txt", "r", encoding="utf-8") as f:
    for line in f:
        filename, link = line.strip().split(",")

        try:
            with open(RAW_FOLDER + filename, "r", encoding="utf-8") as f:
                content = f.read()
                parts = markdown_splitter(content)
                for part in parts:
                    if len(part) > 0:
                        database.append({"filename": filename, "link": link, "content": part})
        except:
            pass

for file in os.listdir(PAGES_FOLDER):
    if file.endswith(".md"):
        with open(PAGES_FOLDER + file, "r", encoding="utf-8") as f:
            content = f.read()
            parts = markdown_splitter(content)
            for part in parts:
                if len(part) > 0:
                    database.append({"filename": file, "link": None, "content": part})

# Save the database
with open("database.json", "w", encoding="utf-8") as f:
    json.dump(database, f, ensure_ascii=False, indent=4)

