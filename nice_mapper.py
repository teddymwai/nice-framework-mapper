#!/usr/bin/env python3
"""
NIST NICE Framework Mapping Engine (SP 800-181 Rev 1, v2.2.0)

Maps scenario telemetry JSON artifacts or assessment question CSVs against
2,211 normalized NIST NICE Task, Knowledge, and Skill (TKS) statements using
TF-IDF cosine similarity and a per-statement usage cap to prevent over-concentration.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "nice_tks_v2_2_0.json"

STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
        "have", "in", "into", "is", "it", "its", "of", "on", "or", "that", "the",
        "their", "them", "this", "to", "using", "via", "with", "within", "without",
        "how", "what", "which", "who", "when", "where", "why", "would", "you",
        "your", "steps", "take", "identify", "describe", "explain",
    }
)

CATEGORY_NAMES = {
    "T": "Task",
    "K": "Knowledge",
    "S": "Skill",
}


def tokenize(text: str) -> list[str]:
    """Normalize and tokenize text into lowercase alphanumeric terms."""
    tokens = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
    out: list[str] = []
    for tok in tokens:
        if tok in STOPWORDS or len(tok) < 2:
            continue
        out.append(tok)
        if "-" in tok:
            for part in tok.split("-"):
                if part not in STOPWORDS and len(part) >= 2:
                    out.append(part)
    return out


class NiceTksMapper:
    """TF-IDF cosine similarity mapper over NIST NICE TKS statements."""

    def __init__(self, tks_rows: list[list[str]]) -> None:
        self.tks_rows = tks_rows
        self.idf: dict[str, float] = {}
        self.vectors: list[tuple[dict[str, float], float]] = []
        self._build_index()

    def _build_index(self) -> None:
        n_docs = len(self.tks_rows)
        doc_freq: Counter[str] = Counter()
        tokenized_docs: list[list[str]] = []

        for row in self.tks_rows:
            tokens = tokenize(row[2])
            tokenized_docs.append(tokens)
            for term in set(tokens):
                doc_freq[term] += 1

        self.idf = {
            term: math.log((n_docs + 1) / (df + 0.5)) + 1.0
            for term, df in doc_freq.items()
        }

        for tokens in tokenized_docs:
            tf = Counter(tokens)
            vec = {term: count * self.idf[term] for term, count in tf.items()}
            norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
            self.vectors.append((vec, norm))

    def _vectorize(self, text: str) -> tuple[dict[str, float], float]:
        tf = Counter(tokenize(text))
        vec = {
            term: count * self.idf[term]
            for term, count in tf.items()
            if term in self.idf
        }
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        return vec, norm

    @staticmethod
    def _cosine(
        a: tuple[dict[str, float], float], b: tuple[dict[str, float], float]
    ) -> float:
        vec_a, norm_a = a
        vec_b, norm_b = b
        if len(vec_a) > len(vec_b):
            vec_a, vec_b = vec_b, vec_a
        dot = sum(w * vec_b[t] for t, w in vec_a.items() if t in vec_b)
        return dot / (norm_a * norm_b)

    @staticmethod
    def score_label(score: float) -> str:
        if score >= 0.22:
            return "strong"
        if score >= 0.10:
            return "moderate"
        return "weak"

    def map_items(
        self, items: list[str], per_item: int = 3, max_reuse: int = 2
    ) -> list[dict[str, Any]]:
        """Map a list of text items (questions or scenario telemetry) to TKS statements."""
        usage = [0] * len(self.tks_rows)
        results: list[dict[str, Any]] = []

        for idx, text in enumerate(items, start=1):
            q_vec = self._vectorize(text)
            scored = sorted(
                (
                    (i, self._cosine(q_vec, doc_vec))
                    for i, doc_vec in enumerate(self.vectors)
                ),
                key=lambda pair: pair[1],
                reverse=True,
            )

            picks: list[tuple[int, float]] = []
            for cand_i, score in scored:
                if len(picks) >= per_item:
                    break
                if usage[cand_i] >= max_reuse or score <= 0:
                    continue
                usage[cand_i] += 1
                picks.append((cand_i, score))

            if len(picks) < min(2, per_item):
                chosen = {c for c, _ in picks}
                for cand_i, score in scored:
                    if len(picks) >= per_item:
                        break
                    if usage[cand_i] >= max_reuse or cand_i in chosen:
                        continue
                    usage[cand_i] += 1
                    picks.append((cand_i, score))
                    chosen.add(cand_i)

            results.append(
                {
                    "index": idx,
                    "input": text,
                    "matches": [
                        {
                            "tks_id": self.tks_rows[i][0],
                            "category": CATEGORY_NAMES.get(
                                self.tks_rows[i][1], self.tks_rows[i][1]
                            ),
                            "statement": self.tks_rows[i][2],
                            "score": round(score, 4),
                            "confidence": self.score_label(score),
                        }
                        for i, score in picks
                    ],
                }
            )
        return results


def load_inputs(input_path: Path) -> tuple[str, list[str]]:
    """Load items from a JSON scenario artifact or CSV question list."""
    suffix = input_path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            scenario_id = str(payload.get("scenario_id", input_path.stem))
            parts: list[str] = []
            for key in ("tags", "milestones", "questions"):
                val = payload.get(key)
                if isinstance(val, list):
                    parts.extend(str(v) for v in val)
            if not parts and "description" in payload:
                parts.append(str(payload["description"]))
            return scenario_id, [" ".join(parts)] if parts else []
        if isinstance(payload, list):
            return input_path.stem, [str(x) for x in payload if str(x).strip()]
        raise ValueError("Unsupported JSON structure.")

    if suffix == ".csv":
        items: list[str] = []
        with input_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            for row_idx, row in enumerate(reader):
                if not row:
                    continue
                cell = row[0].strip()
                if row_idx == 0 and cell.lower() in {"question", "questions", "text"}:
                    continue
                if cell:
                    items.append(cell)
        return input_path.stem, items

    raise ValueError(f"Unsupported input format: {suffix}. Use .json or .csv.")


def export_csv(results: list[dict[str, Any]], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["item_number", "input_text", "tks_id", "category", "statement", "score", "confidence"]
        )
        for item in results:
            for match in item["matches"]:
                writer.writerow(
                    [
                        item["index"],
                        item["input"],
                        match["tks_id"],
                        match["category"],
                        match["statement"],
                        match["score"],
                        match["confidence"],
                    ]
                )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Map scenario telemetry or assessment questions to NIST NICE TKS statements."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to .json or .csv input")
    parser.add_argument(
        "--data", type=Path, default=DEFAULT_DATA_PATH, help="Path to TKS JSON dictionary"
    )
    parser.add_argument("--per-item", type=int, default=3, help="TKS statements per item (2-5)")
    parser.add_argument(
        "--output", type=Path, default=None, help="Optional output path (.json or .csv)"
    )
    args = parser.parse_args()

    tks_rows = json.loads(args.data.read_text(encoding="utf-8"))
    mapper = NiceTksMapper(tks_rows)
    label, items = load_inputs(args.input)
    results = mapper.map_items(items, per_item=max(2, min(5, args.per_item)))

    output_payload = {
        "source": label,
        "framework": "NIST SP 800-181 Rev 1 (NICE v2.2.0)",
        "tks_pool_size": len(tks_rows),
        "results": results,
    }

    if args.output:
        if args.output.suffix.lower() == ".csv":
            export_csv(results, args.output)
        else:
            args.output.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")
        print(f"Wrote {len(results)} mapped item(s) to {args.output}")
    else:
        print(json.dumps(output_payload, indent=2))


if __name__ == "__main__":
    main()
