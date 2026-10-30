"""Deterministic BM25 over Chinese bigrams and Latin words. No embeddings."""
import json
import math
import re
from collections import Counter
from pathlib import Path


DEFAULT_DATA = Path(__file__).resolve().parents[2] / "data" / "documents.json"


def tokenize(text):
    tokens = []
    for part in re.findall(r"[\u4e00-\u9fff]+|[a-z0-9_]+", text.lower()):
        if re.fullmatch(r"[\u4e00-\u9fff]+", part):
            tokens.extend(part[i:i + 2] for i in range(len(part) - 1))
            if len(part) == 1:
                tokens.append(part)
        else:
            tokens.append(part)
    return tokens


class KnowledgeBase:
    def __init__(self, path=DEFAULT_DATA, data=None):
        self.path = Path(path)
        self.data = data if data is not None else json.loads(self.path.read_text(encoding="utf-8"))
        self.documents = {}
        for doc in self.data["documents"]:
            if not isinstance(doc["doc_id"], str) or doc["doc_id"] in self.documents:
                raise ValueError("Duplicate or invalid document ID")
            for key in ("title", "scope", "version_date"):
                if not isinstance(doc[key], str):
                    raise ValueError("Invalid document metadata")
            chunk_ids = set()
            for chunk in doc["chunks"]:
                if not isinstance(chunk["chunk_id"], str) or chunk["chunk_id"] in chunk_ids or not isinstance(chunk["text"], str):
                    raise ValueError("Duplicate or invalid chunk")
                chunk_ids.add(chunk["chunk_id"])
            self.documents[doc["doc_id"]] = doc
        self.counts = {doc_id: Counter(tokenize(doc["title"] + " " + " ".join(c["text"] for c in doc["chunks"])))
                       for doc_id, doc in self.documents.items()}
        self.lengths = {doc_id: sum(count.values()) for doc_id, count in self.counts.items()}
        self.avg_length = sum(self.lengths.values()) / max(len(self.lengths), 1) or 1
        self.df = Counter(term for count in self.counts.values() for term in count)

    def search(self, query, top_k=4):
        terms = set(tokenize(query))
        scored = []
        n = len(self.documents)
        for doc_id, counts in self.counts.items():
            score = 0.0
            for term in terms:
                tf = counts.get(term, 0)
                if tf:
                    idf = math.log(1 + (n - self.df[term] + 0.5) / (self.df[term] + 0.5))
                    norm = tf + 1.5 * (0.25 + 0.75 * self.lengths[doc_id] / self.avg_length)
                    score += idf * tf * 2.5 / norm
            if score > 0:
                doc = self.documents[doc_id]
                snippet = max(doc["chunks"], key=lambda c: len(terms.intersection(tokenize(c["text"]))))
                scored.append({"doc_id": doc_id, "title": doc["title"], "version_date": doc["version_date"],
                               "scope": doc["scope"], "score": round(score, 6),
                               "snippet": dict(snippet)})
        return sorted(scored, key=lambda hit: (-hit["score"], hit["doc_id"]))[:top_k]

    def read(self, doc_id, chunk_id=None):
        if doc_id not in self.documents:
            raise KeyError("Unknown document: " + doc_id)
        doc = self.documents[doc_id]
        chunks = [c for c in doc["chunks"] if chunk_id is None or c["chunk_id"] == chunk_id]
        if not chunks:
            raise KeyError("Unknown chunk: " + str(chunk_id))
        return {key: doc[key] for key in ("doc_id", "title", "version_date", "scope")}, chunks
