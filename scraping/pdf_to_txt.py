import glob
import os
from pathlib import Path
import pdfplumber

FILES_DIR = "./all_files"

for file in glob.glob(os.path.join(FILES_DIR, "*.pdf")):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    with open(os.path.join(FILES_DIR, f"{Path(file).stem}.txt"), "w", encoding="utf-8") as f:
        f.write(text)

