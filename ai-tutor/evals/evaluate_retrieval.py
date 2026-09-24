"""
Retrieval eval harness (Milestone 1, day 5).

Runs every retrieval setup on sets Q and R and reports hit@1, hit@3 and MRR
(teach-first part 5), split by on-page / off-page questions, plus how well the
best cosine score separates answerable from unanswerable questions.

Run from the repo root:
    ai-tutor/.venv/Scripts/python ai-tutor/evals/evaluate_retrieval.py

Writes ai-tutor/evals/results/retrieval.md (the table) and misses.json (every
question whose gold chunk was not in the top 3, for FAILURES.md).

Author: Pixels2GenAI Project
"""

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

EVALS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVALS_DIR.parent))
from retrieval import load_retriever  # noqa: E402  (needs the path set above)

RESULTS_DIR = EVALS_DIR / "results"
SETUPS = [
    ("BM25", "bm25", 0.0),
    ("Dense", "dense", 0.0),
    ("Hybrid (RRF)", "hybrid", 0.0),
    ("Hybrid + boost 0.005 (day 5)", "hybrid", 0.005),
    ("Hybrid + boost 0.01 (chosen on dev)", "hybrid", 0.01),
    ("Hybrid + large boost", "hybrid", 0.03),
]
MRR_DEPTH = 10   # a gold chunk below rank 10 scores 0, as in teach-first part 5


def load_questions(file_name):
    path = EVALS_DIR / file_name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def gold_rank(result_ids, gold):
    """1-based rank of the first gold chunk in the results, or None if absent."""
    for position, chunk_id in enumerate(result_ids, start=1):
        if chunk_id in gold:
            return position
    return None


def right_lesson_in_top3(result_ids, gold):
    """Secondary metric: a gold LESSON appears in the top 3, even if the section differs.

    For a tutor that is already useful (the model reads the chunk, the link lands on
    the right page), but the section-level hit@3 stays the headline number.
    """
    gold_lessons = {chunk_id.split("#")[0] for chunk_id in gold}
    return any(chunk_id.split("#")[0] in gold_lessons for chunk_id in result_ids[:3])


def summarise(outcomes):
    """Metrics from a list of (gold rank or None, right lesson in top 3) pairs."""
    if not outcomes:
        return None
    ranks = [rank for rank, _ in outcomes]
    return {
        "n": len(ranks),
        "hit@1": sum(1 for rank in ranks if rank == 1) / len(ranks),
        "hit@3": sum(1 for rank in ranks if rank and rank <= 3) / len(ranks),
        "mrr": sum(1 / rank for rank in ranks if rank) / len(ranks),
        "lesson@3": sum(1 for _, lesson_hit in outcomes if lesson_hit) / len(ranks),
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    retriever = load_retriever()
    # Set Q is split once (fixed seed, stratified by kind and style): settings such as
    # the boost size are chosen on 'Q dev' only; 'Q test' is the number we report.
    set_q = load_questions("set_q.jsonl")
    question_sets = {
        "Q dev": [q for q in set_q if q.get("split") == "dev"],
        "Q test": [q for q in set_q if q.get("split") == "test"],
        "R": load_questions("set_r.jsonl"),
    }
    if (EVALS_DIR / "set_t.jsonl").exists():
        question_sets["T"] = load_questions("set_t.jsonl")

    table_rows = []
    misses = []
    cosine_by_kind = {"answerable": [], "unanswerable": []}

    for set_name, questions in question_sets.items():
        answerable = [q for q in questions if q["gold"]]
        for label, setup, boost in SETUPS:
            ranks_by_kind = {"all": [], "on_page": [], "off_page": []}
            for question in answerable:
                results, best_cosine = retriever.search(
                    question["question"], setup, question["asked_on"], boost, top_k=MRR_DEPTH
                )
                result_ids = [retriever.chunks[index]["id"] for index, _ in results]
                rank = gold_rank(result_ids, set(question["gold"]))
                outcome = (rank, right_lesson_in_top3(result_ids, question["gold"]))
                ranks_by_kind["all"].append(outcome)
                ranks_by_kind.setdefault(question.get("kind", "on_page"), []).append(outcome)
                if setup == "hybrid" and boost == 0.01 and (rank is None or rank > 3):
                    misses.append({
                        "set": set_name, "id": question["id"], "asked_on": question["asked_on"],
                        "kind": question.get("kind", "on_page"), "question": question["question"],
                        "gold": question["gold"], "gold_rank": rank, "got_top3": result_ids[:3],
                    })
            table_rows.append((set_name, label, {kind: summarise(r) for kind, r in ranks_by_kind.items()}))

        # Unanswerable detection uses the best cosine, which doesn't depend on the setup.
        for question in questions:
            _, best_cosine = retriever.search(question["question"], "dense", top_k=1)
            kind = "answerable" if question["gold"] else "unanswerable"
            cosine_by_kind[kind].append((best_cosine, question["id"]))

    # ---- report ----
    lines = [f"# Retrieval results ({date.today().isoformat()})", ""]
    lines.append(f"Chunks: {len(retriever.chunks)}. Model: bge-small-en-v1.5. "
                 "Hit@k = gold chunk in the top k; MRR averaged over answerable questions (depth 10).")
    for set_name in question_sets:
        lines += ["", f"## Set {set_name}", "",
                  "| Setup | hit@1 | hit@3 | MRR | lesson@3 | hit@3 on-page | hit@3 off-page |",
                  "|---|---|---|---|---|---|---|"]
        for row_set, label, stats in table_rows:
            if row_set != set_name:
                continue
            overall = stats["all"]
            on_page = stats.get("on_page")
            off_page = stats.get("off_page")
            lines.append(
                f"| {label} | {overall['hit@1']:.0%} | {overall['hit@3']:.0%} | {overall['mrr']:.2f} "
                f"| {overall['lesson@3']:.0%} "
                f"| {on_page['hit@3']:.0%} (n={on_page['n']}) | "
                + (f"{off_page['hit@3']:.0%} (n={off_page['n']})" if off_page else "n/a") + " |"
            )

    answerable_cos = np.array([score for score, _ in cosine_by_kind["answerable"]])
    unanswerable = sorted(cosine_by_kind["unanswerable"], reverse=True)
    lines += ["", "## Unanswerable detection (best cosine score)", "",
              f"- Answerable questions: min {answerable_cos.min():.3f}, "
              f"10th percentile {np.percentile(answerable_cos, 10):.3f}, median {np.median(answerable_cos):.3f}",
              "- Unanswerable questions: " + ", ".join(f"{qid} {score:.3f}" for score, qid in unanswerable)]
    threshold = max(score for score, _ in unanswerable) if unanswerable else None
    if threshold is not None:
        caught_wrongly = int((answerable_cos <= threshold).sum())
        lines.append(f"- A threshold just above the highest unanswerable score ({threshold:.3f}) would also "
                     f"reject {caught_wrongly} of {len(answerable_cos)} answerable questions.")

    RESULTS_DIR.mkdir(exist_ok=True)
    report = "\n".join(lines) + "\n"
    (RESULTS_DIR / "retrieval.md").write_text(report, encoding="utf-8")
    (RESULTS_DIR / "misses.json").write_text(json.dumps(misses, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report)
    print(f"{len(misses)} misses (hybrid + boost 0.01, gold not in top 3) -> results/misses.json")


if __name__ == "__main__":
    main()
