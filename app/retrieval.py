"""Deterministic lexical vectors + BM25 + rank fusion; no neural-model claim."""
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).lower()).strip()


def grams(text: str, sizes=(3,)) -> list[str]:
    text = normalize(text)
    return [text[i:i+n] for n in sizes for i in range(max(0, len(text)-n+1)) if text[i:i+n].strip()]


def tokens(text: str) -> list[str]:
    text = normalize(text)
    english = re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", text)
    thai = [g for segment in re.findall(r"[\u0e00-\u0e7f]+", text) for g in grams(segment, (2,))]
    return english + thai


def rrf(rank_lists, k=60):
    scores = {}
    for ranked in rank_lists:
        for rank, doc_id in enumerate(ranked, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


class Retriever:
    def __init__(self, path: Path | None = None):
        path = path or ROOT / "data/policies.json"
        self.documents = json.loads(path.read_text(encoding="utf-8"))
        self.by_id = {d["id"]: d for d in self.documents}
        texts = [d["title"] + " " + d["text"] + " " + d["english"] for d in self.documents]
        self.tf = [Counter(grams(text)) for text in texts]
        self.lexical = [Counter(tokens(text)) for text in texts]
        n = len(texts)
        df = Counter(g for doc in self.tf for g in doc)
        self.idf = {g: math.log((n+1)/(f+1))+1 for g, f in df.items()}
        self.vectors = [self._vector(t) for t in self.tf]
        self.norms = [math.sqrt(sum(v*v for v in vector.values())) for vector in self.vectors]
        self.df = Counter(t for doc in self.lexical for t in doc)
        self.lengths = [sum(doc.values()) for doc in self.lexical]
        self.avg_length = sum(self.lengths) / n

    def _vector(self, counts):
        return {term: (1+math.log(freq))*self.idf[term] for term, freq in counts.items() if term in self.idf}

    def rankings(self, query: str):
        q = self._vector(Counter(grams(query)))
        norm = math.sqrt(sum(v*v for v in q.values()))
        cosine, bm25 = {}, {}
        terms = set(tokens(query))
        n = len(self.documents)
        for i, doc in enumerate(self.documents):
            cosine[doc["id"]] = sum(v*self.vectors[i].get(t, 0) for t, v in q.items()) / (norm*self.norms[i]) if norm and self.norms[i] else 0.0
            score = 0.0
            for term in terms:
                freq = self.lexical[i].get(term, 0)
                if not freq:
                    continue
                df = self.df[term]
                idf = math.log(1 + (n-df+0.5)/(df+0.5))
                score += idf * freq * 2.5 / (freq + 1.5*(0.25+0.75*self.lengths[i]/self.avg_length))
            bm25[doc["id"]] = score
        return cosine, bm25

    def search(self, query: str, top_k=3, method="hybrid", min_score=0.04):
        cosine, bm25 = self.rankings(query)
        vector_rank = sorted((d for d in cosine if cosine[d] > 0), key=cosine.get, reverse=True)
        bm25_rank = sorted((d for d in bm25 if bm25[d] > 0), key=bm25.get, reverse=True)
        if method == "vector":
            ranked = vector_rank
        elif method == "bm25":
            ranked = bm25_rank
        elif method == "hybrid":
            ranked = rrf([vector_rank[:10], bm25_rank[:10]])
        else:
            raise ValueError("Unknown retrieval method")
        # Threshold is on interpretable cosine, never on the incomparable RRF score.
        ranked = [d for d in ranked if cosine[d] >= min_score]
        return [{**self.by_id[d], "score": round(cosine[d], 5), "source": f"data/policies.json#{d}"} for d in ranked[:top_k]]
