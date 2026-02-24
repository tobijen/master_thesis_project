import json
import random
from typing import Any, Tuple

# Eingabe- und Ausgabepfade
INPUT_FILE = "./data/processed/gpt_judgments_expertsearch_testcollection.json"
OUTPUT_FILE = "./data/processed/human_judgements.json"

# Anzahl der zufällig zu ziehenden Suchanfragen
N_QUERIES = 8

# Seed zur Sicherstellung der Reproduzierbarkeit
RANDOM_SEED = 42

# Felder innerhalb eines Judgments, die JSON-kodierte Strings enthalten können
FIELDS_TO_PARSE = ("expert",)


def parse_maybe_json_string(value: Any) -> Any:
    """
    Parst einen JSON-kodierten String in ein Python-Objekt.
    Gibt den ursprünglichen Wert zurück, falls keine gültige JSON-Struktur vorliegt.
    """
    if not isinstance(value, str):
        return value

    value = value.strip()
    if not value:
        return value

    if not (
        (value.startswith("{") and value.endswith("}"))
        or (value.startswith("[") and value.endswith("]"))
    ):
        return value

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def transform_sampled_queries(sampled_queries: list) -> Tuple[list, int, int]:
    """
    Führt strukturierende Transformationen auf den ausgewählten Queries durch:
    - Konvertiert JSON-kodierte Felder (z.B. expert) in native Python-Objekte
    - Ergänzt jedes Dokument um das Feld 'human_judgement'
    - Entfernt das Feld 'result_status', sofern vorhanden
    """
    converted_count = 0
    failed_count = 0

    for query_item in sampled_queries:
        judgments = query_item.get("judgments")
        if not isinstance(judgments, list):
            continue

        for judgment in judgments:
            if not isinstance(judgment, dict):
                continue

            # Konvertierung definierter JSON-String-Felder
            for field in FIELDS_TO_PARSE:
                if field not in judgment:
                    continue

                original_value = judgment[field]
                parsed_value = parse_maybe_json_string(original_value)

                if isinstance(original_value, str) and not isinstance(parsed_value, str):
                    judgment[field] = parsed_value
                    converted_count += 1
                elif isinstance(original_value, str):
                    value = original_value.strip()
                    if (
                        (value.startswith("{") and value.endswith("}"))
                        or (value.startswith("[") and value.endswith("]"))
                    ):
                        failed_count += 1

            # Initialisierung des Human-Judgments
            judgment.setdefault("human_judgement", None)

            # Entfernen technischer Statusinformationen
            judgment.pop("result_status", None)

    return sampled_queries, converted_count, failed_count


def main():
    random.seed(RANDOM_SEED)

    # Einlesen der vollständigen Testkollektion
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validierung der erwarteten Datenstruktur
    if not isinstance(data, list):
        raise ValueError("Die Eingabedatei muss eine Liste von Suchanfragen enthalten.")

    if len(data) < N_QUERIES:
        raise ValueError(
            f"Nicht genügend Suchanfragen vorhanden ({len(data)} < {N_QUERIES})."
        )

    # Zufällige Auswahl vollständiger Query-Einträge
    sampled_queries = random.sample(data, N_QUERIES)

    # Transformation der ausgewählten Queries
    sampled_queries, converted, failed = transform_sampled_queries(sampled_queries)

    # Schreiben der Stichprobe in die Ausgabedatei
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sampled_queries, f, ensure_ascii=False, indent=2)

    print(f"Ausgabedatei erstellt: {OUTPUT_FILE}")
    print(f"Erfolgreich konvertierte Felder: {converted}")
    print(f"Nicht parsbare JSON-Felder: {failed}")


if __name__ == "__main__":
    main()
