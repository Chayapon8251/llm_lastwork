import hashlib
import json
from pathlib import Path
from app.retrieval import Retriever

ROOT = Path(__file__).resolve().parents[1]


def metrics(ranked, relevant, k):
    relevant = set(relevant)
    ranked = ranked[:k]
    hits = len(set(ranked) & relevant)
    rr = next((1/r for r, doc in enumerate(ranked, 1) if doc in relevant), 0.0)
    return {"recall": hits/len(relevant) if relevant else 0.0, "precision": hits/k, "mrr": rr, "complete": float(relevant <= set(ranked))}


def evaluate():
    cases = json.loads((ROOT / "eval/test.json").read_text(encoding="utf-8"))
    retrieval = Retriever()
    systems = [("vector_top1", "vector", 1), ("vector_top3", "vector", 3), ("bm25_top3", "bm25", 3), ("hybrid_top3", "hybrid", 3)]
    rows = []
    for name, method, k in systems:
        details = []
        for case in cases:
            ranked = [d["id"] for d in retrieval.search(case["query"], k, method)]
            details.append({**case, "ranked": ranked, **metrics(ranked, case["relevant"], k)})
        averages = {m: round(sum(d[m] for d in details)/len(details), 4) for m in ("recall", "precision", "mrr", "complete")}
        groups = {}
        for group in sorted({d["group"] for d in details}):
            subset = [d for d in details if d["group"] == group]
            groups[group] = {"n": len(subset), **{m: round(sum(d[m] for d in subset)/len(subset), 4) for m in averages}}
        rows.append({"system": name, "cutoff": k, **averages, "groups": groups, "details": details})
    hashes = {p: hashlib.sha256((ROOT/p).read_text(encoding="utf-8-sig").replace("\r\n", "\n").encode("utf-8")).hexdigest() for p in ("data/policies.json", "eval/test.json", "app/retrieval.py")}
    result = {"benchmark": "GearMate curated lexical retrieval v1", "n": len(cases), "llm_evaluated": False, "config": {"vector": "character-trigram TF-IDF, not neural embeddings", "rrf_k": 60, "cosine_floor": 0.04, "candidate_limit_per_retriever": 10, "selected_method": "vector_top3", "hash_normalization": "UTF-8 without BOM, LF newlines"}, "hashes": hashes, "systems": rows}
    output = ROOT / "results/retrieval.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("System           cutoff  recall   precision  MRR     all-relevant")
    for row in rows:
        print(f"{row['system']:<17}{row['cutoff']:<8}{row['recall']:<9.4f}{row['precision']:<11.4f}{row['mrr']:<8.4f}{row['complete']:.4f}")
    print("No LLM calls. See results/retrieval.json for every query and failure.")
    return result


if __name__ == "__main__":
    evaluate()
