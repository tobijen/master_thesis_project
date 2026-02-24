# This code is used to compute the agreement between the judgements of the human expert and the LLM.
# Specifically Cohen's Kappa is computed to measure the agreement and a Confusion Matrix is generated to visualize the agreement.

import json
import os

from umbrela_models.utils.common_utils import calculate_kappa, draw_confusion_matrix

# Pfad zur Datei
judgements_path = "./data/processed/human_judgement.json"

# JSON direkt einlesen
with open(judgements_path, "r", encoding="utf-8") as f:
    human_judgements = json.load(f)


def create_judgment_lists(human_judgements):
    human_labels = []
    model_labels = []

    for query_item in human_judgements:
        if "judgments" not in query_item:
            print("No judgments found for query:", query_item.get("query", "N/A"))
            continue

        for judgment in query_item["judgments"]:
            human_judgment = judgment.get("human_judgement")
            model_judgment = judgment.get("judgment")

            human_labels.append(human_judgment)
            model_labels.append(model_judgment)

    assert len(human_labels) == len(model_labels), "Length mismatch between human and model labels"
    
    return human_labels, model_labels

human_labels, model_labels = create_judgment_lists(human_judgements)

print(human_labels)
print(model_labels)

print("Calculating Cohen's Kappa...")

calculate_kappa(human_labels, model_labels)


print("Drawing Confusion Matrix...")

draw_confusion_matrix(human_labels, model_labels, "Expertsearch agreement", "GPT-5-mini")
