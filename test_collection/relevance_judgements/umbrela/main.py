from umbrela_models.gpt_judge import GPTJudge
from dotenv import load_dotenv
import json
from umbrela_models.utils import common_utils
from tqdm import tqdm
import os

load_dotenv()


# Pfad zur Datei
query_path = "./data/raw/suchanfragen_testkollektion_final.json"
document_pool_path = "./data/raw/pooling_results_final.json"
output_path_relevance = "./data/processed/gpt_judgments_expertsearch_testcollection.json"

# JSON direkt einlesen
with open(query_path, "r", encoding="utf-8") as f:
    queries_testcollection = json.load(f)

with open(document_pool_path, "r", encoding="utf-8") as f:
    document_pool_testcollection = json.load(f)


# print(len(document_pool_testcollection))

# count = 0
# for obj in document_pool_testcollection:
#     if (
#         isinstance(obj, dict)
#         and "doc_raw" in obj.keys()
#         and "full_text" in obj["doc_raw"]
#     ):
#         count += 1
#         print(obj["doc_raw"])
# print("----- ", count , " -----")


# print("Anzahl der Objekte mit 'doc_raw' als String und 'full_text' darin:", count)

input_dicts = common_utils.create_input_dicts(queries_testcollection, document_pool_testcollection)

if os.path.exists(output_path_relevance):
    with open(output_path_relevance, "r", encoding="utf-8") as f:
        rel_judgements = json.load(f)
else:
    rel_judgements = []

for input_dict in tqdm(input_dicts):

    print("QUERY:", input_dict["query"]["text"])

    query_exists = any(
    entry.get("query") == input_dict["query"]["text"]
    for entry in rel_judgements
    )

    if query_exists:
        print("Already judged, skipping...")
        continue

    judge_gpt = GPTJudge(
        qrel="qrel-expertsearch",
        prompt_type="expert",
        model_name="gpt-5-mini-2025-08-07"
    )

    judgments = judge_gpt.judge(request_dict=input_dict)

    judgments_dict = {
        "query": input_dict["query"]["text"],
        "query_id": input_dict["query"]["qid"],
        "judgments": judgments
    }

    rel_judgements.append(judgments_dict)

    with open(output_path_relevance, "w", encoding="utf-8") as f:
        json.dump(rel_judgements, f, ensure_ascii=False, indent=2)
