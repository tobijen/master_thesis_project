import json
from pathlib import Path

def load_json(path: str):
    """
    Load a JSON file from disk.

    Parameters
    ----------
    path : str
        Path to the JSON file.

    Returns
    -------
    object
        Parsed JSON content.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def dump_json(path: str, data):
    """
    Write a Python object to disk as a formatted JSON file.

    Parameters
    ----------
    path : str
        Output file path.
    data : object
        JSON-serializable Python object.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_expert_id(expert_json_str: str) -> str | None:
    """
    Extract the expert identifier from a serialized expert JSON string.

    Parameters
    ----------
    expert_json_str : str
        JSON string representation of an expert profile.

    Returns
    -------
    str or None
        The expert ID if present, otherwise None.
    """
    try:
        return json.loads(expert_json_str).get("id")
    except Exception:
        return None

def build_indexes(input_dicts):
    """
    Build lookup indexes from the original input data used for judgment creation.

    The function constructs:
    - a mapping from query text to query ID (qid)
    - a mapping from (query text, expert ID) to document ID (docid)

    Parameters
    ----------
    input_dicts : list
        Parsed content of input_dicts_gpt_judge.json.

    Returns
    -------
    tuple
        (qtext_to_qid, qtext_expertid_to_docid)
    """
    qtext_to_qid = {}
    qtext_expertid_to_docid = {}

    for item in input_dicts:
        qtext = item["query"]["text"]
        qid = item["query"]["qid"]
        qtext_to_qid[qtext] = qid

        for cand in item.get("candidates", []):
            doc_str = cand.get("doc", "")
            docid = cand.get("docid")
            expert_id = parse_expert_id(doc_str)
            if expert_id is not None:
                qtext_expertid_to_docid[(qtext, expert_id)] = docid

    return qtext_to_qid, qtext_expertid_to_docid

def enrich(gpt_judgments, qtext_to_qid, qtext_expertid_to_docid):
    """
    Enrich GPT-based relevance judgments with query and expert identifiers.

    For each judgment entry:
    - the query ID is resolved via the query text
    - the expert (document) ID is resolved via the expert identifier

    Parameters
    ----------
    gpt_judgments : list
        Parsed content of gpt_judgments_expertsearch_testcollection.json.
    qtext_to_qid : dict
        Mapping from query text to query ID.
    qtext_expertid_to_docid : dict
        Mapping from (query text, expert ID) to document ID.

    Returns
    -------
    list
        List of unresolved mappings encountered during enrichment.
    """
    misses = []
    for entry in gpt_judgments:
        qtext = entry["query"]

        # Resolve and assign query ID
        qid = qtext_to_qid.get(qtext)
        if qid is None:
            misses.append(("missing_qid", qtext))
        else:
            entry["query_id"] = qid

        # Resolve and assign expert (document) IDs
        for j in entry.get("judgments", []):
            expert_id = parse_expert_id(j.get("expert", ""))
            if expert_id is None:
                misses.append(("missing_expert_id_in_judgment", qtext))
                continue

            docid = qtext_expertid_to_docid.get((qtext, expert_id))
            if docid is None:
                misses.append(("missing_docid_for_pair", qtext, expert_id))
            else:
                j["expert_id"] = docid
                # Optional: store query ID at judgment level for downstream processing
                j["query_id"] = qid

    return misses

def main():
    """
    Execute the ID enrichment pipeline.

    Loads the original input definitions and GPT-generated judgments,
    resolves query and expert identifiers, and writes an enriched
    judgment file to disk.
    """
    input_path = "./data/processed/input_dicts_gpt_judge.json"
    judgments_path = "./data/processed/gpt_judgments_expertsearch_testcollection.json"
    out_path = "./data/processed/gpt_judgments_expertsearch_testcollection_enriched.json"

    input_dicts = load_json(input_path)
    print(f"✅ Input geladen: {input_path} ({len(input_dicts)} Einträge)")
    gpt_judgments = load_json(judgments_path)
    print(f"✅ GPT-Judgments geladen: {judgments_path} ({len(gpt_judgments)} Einträge)")

    qtext_to_qid, qtext_expertid_to_docid = build_indexes(input_dicts)
    misses = enrich(gpt_judgments, qtext_to_qid, qtext_expertid_to_docid)

    dump_json(out_path, gpt_judgments)

    print(f"✅ Output geschrieben: {out_path}")
    print(f"✅ Queries im Index: {len(qtext_to_qid)}")
    print(f"✅ (Query, Expert)-Paare im Index: {len(qtext_expertid_to_docid)}")
    print(f"⚠️ Misses: {len(misses)}")
    if misses:
        print("Beispiele (max 20):")
        for m in misses[:20]:
            print(m)

if __name__ == "__main__":
    main()
