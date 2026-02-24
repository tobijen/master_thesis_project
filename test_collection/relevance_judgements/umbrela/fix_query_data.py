import json
from pathlib import Path


# input and output paths
query_path = Path(
    "./data/raw/suchanfragen_testkollektion_final.json"
)

# input and output paths
query_path_fixed = Path(
    "./data/raw/suchanfragen_testkollektion_final_fixed.json"
)
with open(query_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# wenn du wieder als JSON speichern willst, aber mit echten Umlauten:
with open(query_path_fixed, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)