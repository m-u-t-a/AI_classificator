import fitz
import re

def category_extractor(pdf_path):
    doc = fitz.open(pdf_path)

    result = {}
    key = None
    flag = False
    value = ''
    for page in doc.pages(1, len(doc), 1):
        blocks = page.get_text("dict")
        regex = r'^\d{4}\.\d{4}\.\d{4}\.\d{4}$'
        for block in blocks["blocks"]:
            for lines in block["lines"]:
                for span in lines["spans"]:
                    if re.match(regex, span['text']) and span['text'][-1] != '0':
                        if key:
                            value = value[1:]
                            result[key] = value
                            value = ''
                        key = span['text']
                        flag = True
                    elif flag and span['origin'][0] != 76.69998168945312:
                        value += " "
                        value += span['text']
                    elif span['origin'][0] == 76.69998168945312:
                        if key:
                            value = value[1:]
                            result[key] = value
                            value = ''
                            key = None
                            flag = False
    return result
