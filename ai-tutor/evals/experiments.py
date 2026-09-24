"""
Day-6 retrieval experiments, judged on the DEV half of set Q only.

Each experiment changes one setting from the baseline (hybrid + boost 0.005).
Because off-page questions are scarce (follow-ups #5), every setting is judged on
on-page and off-page hit@3 separately, and on their average ("balanced"), never
on the overall score alone.

Run from the repo root (needs data/embeddings-all.npy and data/embeddings-none.npy):
    ai-tutor/.venv/Scripts/python ai-tutor/evals/experiments.py

Writes ai-tutor/evals/results/experiments.md.

Author: Pixels2GenAI Project
"""

import json
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVALS_DIR.parent))
from retrieval import load_retriever  # noqa: E402

BASELINE = {"bm25_code": "all", "dense_code": "all", "type_weights": None, "boost": 0.005}

EXPERIMENTS = [
    ("Baseline", {}),
    # Pattern 1 in the misses: Overview / Summary beat the real section.
    ("Summary + overview x0.8", {"type_weights": {"summary": 0.8, "overview": 0.8}}),
    ("Summary + overview x0.6", {"type_weights": {"summary": 0.6, "overview": 0.6}}),
    ("Summary + overview removed", {"type_weights": {"summary": 0.0, "overview": 0.0}}),
    # Pattern 2: long exercise chunks match almost anything.
    ("Exercises x0.8", {"type_weights": {"exercise": 0.8}}),
    ("BM25 without solution code", {"bm25_code": "outside_dropdowns"}),
    ("BM25 prose only", {"bm25_code": "none"}),
    # Small embedding models handle code poorly.
    ("Dense prose only", {"dense_code": "none"}),
]
BOOSTS = [0.0, 0.002, 0.005, 0.01, 0.02]


def load_dev():
    rows = [json.loads(line) for line in (EVALS_DIR / "set_q.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return [row for row in rows if row.get("split") == "dev" and row["gold"]]


def score(retriever, questions, boost):
    """hit@3 overall, on-page, off-page, and MRR (depth 10)."""
    hits = {"on_page": [], "off_page": []}
    reciprocal_ranks = []
    for question in questions:
        results, _ = retriever.search(question["question"], "hybrid", question["asked_on"], boost, top_k=10)
        ids = [retriever.chunks[index]["id"] for index, _ in results]
        rank = next((position for position, chunk_id in enumerate(ids, 1) if chunk_id in question["gold"]), None)
        hits[question["kind"]].append(bool(rank and rank <= 3))
        reciprocal_ranks.append(1 / rank if rank else 0)
    on_page = sum(hits["on_page"]) / len(hits["on_page"])
    off_page = sum(hits["off_page"]) / len(hits["off_page"])
    overall = (sum(hits["on_page"]) + sum(hits["off_page"])) / len(questions)
    return {"overall": overall, "on": on_page, "off": off_page, "balanced": (on_page + off_page) / 2,
            "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks)}


def row(label, result):
    return (f"| {label} | {result['overall']:.0%} | {result['on']:.0%} | {result['off']:.0%} "
            f"| {result['balanced']:.0%} | {result['mrr']:.2f} |")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    dev = load_dev()
    n_on = sum(q["kind"] == "on_page" for q in dev)
    n_off = sum(q["kind"] == "off_page" for q in dev)
    header = ["| Setting | hit@3 | on-page | off-page | balanced | MRR |", "|---|---|---|---|---|---|"]
    lines = ["# Retrieval experiments (set Q dev)", "",
             f"{len(dev)} answerable dev questions: {n_on} on-page, {n_off} off-page. "
             f"One on-page question = {1 / n_on:.0%}, one off-page question = {1 / n_off:.0%}. "
             "Balanced = mean of on-page and off-page hit@3.", "",
             "## One change at a time (boost 0.005)", ""] + header

    cache = {}
    for label, change in EXPERIMENTS:
        settings = {**BASELINE, **change}
        key = (settings["bm25_code"], settings["dense_code"], json.dumps(settings["type_weights"], sort_keys=True))
        if key not in cache:
            cache[key] = load_retriever(settings["bm25_code"], settings["dense_code"],
                                        settings["type_weights"], use_defaults=False)
        result = score(cache[key], dev, settings["boost"])
        lines.append(row(label, result))
        print(lines[-1])

    lines += ["", "## Boost sweep (baseline settings)", ""] + header
    baseline_retriever = cache[("all", "all", "null")]
    for boost in BOOSTS:
        result = score(baseline_retriever, dev, boost)
        lines.append(row(f"boost {boost}", result))
        print(lines[-1])

    (EVALS_DIR / "results").mkdir(exist_ok=True)
    (EVALS_DIR / "results" / "experiments.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
