import os

import re

def extract_fields(fields):
    new = fields.split(sep='\n', maxsplit=-1)
    pattern = r":\s*(.*)"

    result = {}
    for item in new:
        match = re.search(pattern, item)
        if match:
            key = item.split(':')[0].strip()
            value = match.group(1).strip()
            if key == "email":
                key = "e-mail"
            if key == "населённый_пункт":
                key = "населенный_пункт"
            result[key] = value

    # key2, value2 = full_appeal.split(sep=': ', maxsplit=--1)
    # result[key2] = value2
    return result
