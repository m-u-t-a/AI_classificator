import fitz
import pytesseract
from PIL import Image
import io
import json
import os
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path, use_ocr=True, dpi=300):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]

        text = page.get_text()

        if text.strip() and not use_ocr:
            full_text += f"\n--- Страница {page_num + 1} ---\n{text}\n"
        else:
            try:
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")

                image = Image.open(io.BytesIO(img_data))

                text = pytesseract.image_to_string(image, lang='rus+eng')
                full_text += f"\n--- Страница {page_num + 1} ---\n{text}\n"

            except Exception as e:
                full_text += f"\n--- Страница {page_num + 1} ---\nОшибка: {str(e)}\n"

    doc.close()
    return full_text


def save_to_json(all_texts, output_file):

    data = {
        "metadata": {
            "total_files": len(all_texts)
        },
        "documents": []
    }

    for id in all_texts:
        text = all_texts[id]
        data["documents"].append({
            "id": id,
            "text": text
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

pattern = r'\{([^}]*)\}'
texts = {}

for root, dirs, files in os.walk('C:/Users/USER/Обращение январь 2025'):
    for name in files:
        id = re.findall(pattern, root)[0]
        text = extract_text_from_pdf(root + "\\" + name)
        texts[id] = text

save_to_json(texts, "documents.json")
