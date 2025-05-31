import os
import re
import shutil
from pathlib import Path

from rag_pipeline.constants import DATA_PATH

# Base directories
source_base = DATA_PATH
destination_base = "./benchmarking/clean_dataset"
usecases = ["gewerbe", "kfz", "meldebescheinigung", "personalausweis", "wohnsitz_umzug"]

if os.path.exists(destination_base):
    shutil.rmtree(destination_base)

os.mkdir(destination_base)

# Iterate through usecase1 to usecase4
for i in range(0, 5):
    source_dir = os.path.join(source_base, usecases[i])
    dest_dir = os.path.join(destination_base, usecases[i])

    os.mkdir(dest_dir)

    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        if Path(source_file).is_file() and filename[-3:] == ".md":
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Strip whitespace and remove double+ newlines
            stripped = content.strip()
            cleaned = re.sub(r"\n{2,}", "\n", stripped)

            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(cleaned)

print("Processing complete.")
