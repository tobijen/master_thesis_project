import json
import csv
from pathlib import Path

# input and output paths
judgements_path = Path(
    "./data/processed/gpt_judgments_expertsearch_testcollection_enriched.json"
)
output_csv_path = Path("./data/processed/qrels.csv")

# load json file
with judgements_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

# iterate over queries
for query_obj in data:
    query_id = query_obj.get("query_id")
    judgments = query_obj.get("judgments", [])

    # iterate over judgments per query
    for judgment in judgments:
        qid = query_id or judgment.get("query_id")
        expert_id = judgment.get("expert_id")
        score = judgment.get("judgment")

        # skip incomplete entries
        if qid is None or expert_id is None or score is None:
            continue

        rows.append(
            {
                "query_id": qid,
                "doc_id": expert_id,
                "judgment_score": score,
            }
        )

# ensure output directory exists
output_csv_path.parent.mkdir(parents=True, exist_ok=True)

# write csv file
with output_csv_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["query_id", "doc_id", "judgment_score"],
    )
    writer.writeheader()
    writer.writerows(rows)

# optional sanity check
print(f"rows written: {len(rows)}")
