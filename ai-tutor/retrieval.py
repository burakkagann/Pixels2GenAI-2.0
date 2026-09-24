"""
Retrieval: find the lesson chunks that best answer a learner's question.

Four setups (teach-first parts 2-4, Milestone 1 day 4):
  bm25     keyword search: exact words, strong on code names like np.kron
  dense    embedding search: meaning, strong on everyday wording
  hybrid   both, merged with Reciprocal Rank Fusion (ranks, not scores)
  hybrid + boost   hybrid plus a bonus for the lesson the learner is on

Build the embedding index once (after every chunker run):
    ai-tutor/.venv/Scripts/python ai-tutor/retrieval.py --build
Try a question:
    ai-tutor/.venv/Scripts/python ai-tutor/retrieval.py "why are my stars spread evenly?" 2.1.4

Author: Pixels2GenAI Project
"""

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

TUTOR_DIR = Path(__file__).resolve().parent
CHUNKS_FILE = TUTOR_DIR / "data" / "chunks.json"
MODEL_CACHE = TUTOR_DIR / ".cache" / "fastembed"

# Small English model (67 MB, 384 numbers per vector), runs locally with ONNX, so
# learner questions never leave the server. Changing it means rebuilding the index
# (flashcard 4): vectors from two different models are not comparable.
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Reciprocal Rank Fusion constant; 60 is the value from the original RRF paper
# (Cormack et al., 2009) and stops rank 1 from counting far more than rank 2.
RRF_K = 60

# Lessons use British spelling in prose and American spelling in code (colour/color).
# BM25 treats them as different words, so both sides are mapped to one spelling.
SPELLING_VARIANTS = {
    "colour": "color", "colours": "colors", "coloured": "colored",
    "grey": "gray", "greyscale": "grayscale",
    "centre": "center", "centred": "centered", "centres": "centers",
    "neighbour": "neighbor", "neighbours": "neighbors",
    "normalise": "normalize", "normalised": "normalized",
    "visualise": "visualize", "optimise": "optimize", "behaviour": "behavior",
}


# ---------------------------------------------------------------------------
# Text preparation
# ---------------------------------------------------------------------------
CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
DROPDOWN_BLOCK = re.compile(r"<Dropdown\b.*?</Dropdown>", re.DOTALL)


def search_text(chunk, code="all"):
    """The text that search sees for one chunk.

    Lesson title and section title go first: they are the most compact summary of
    what the chunk is about. JSX tags like <Figure alt="..." caption="..."/> are
    replaced by their quoted values, so the alt text and captions stay searchable
    but tag names ('Figure', 'Dropdown') don't pollute every chunk.

    code: which code blocks to keep (a Milestone 1 day-6 experiment)
      "all"                keep every code block
      "outside_dropdowns"  drop code inside hint/solution dropdowns (full solutions
                           make exercise chunks match almost any question)
      "none"               prose only (small embedding models handle code poorly)
    """
    text = chunk["text"]
    if code == "outside_dropdowns":
        text = DROPDOWN_BLOCK.sub(lambda block: CODE_BLOCK.sub(" ", block.group()), text)
    elif code == "none":
        text = CODE_BLOCK.sub(" ", text)
    body = re.sub(
        r"</?[A-Za-z][^<>]*>",   # a tag starts with a letter; 'x < 5' in code does not
        lambda tag: " ".join(re.findall(r'"([^"]*)"', tag.group())),
        text,
    )
    return f"{chunk['lesson_title']}. {chunk['title']}.\n{body}"


def tokenize(text):
    """Split text into BM25 words.

    Keeps dotted code names whole ('np.random.normal') AND adds their parts
    ('np', 'random', 'normal'), so both 'np.random.normal' and 'normal' match.
    """
    tokens = []
    for word in re.findall(r"[a-z0-9_]+(?:\.[a-z0-9_]+)*", text.lower()):
        parts = word.split(".") if "." in word else []
        for token in [word] + parts:
            token = SPELLING_VARIANTS.get(token, token)
            # Crude plural stripping so 'stars' matches 'star'. Applied to both the
            # lessons and the questions, so an odd result ('canvas' -> 'canva') still matches.
            if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
                token = token[:-1]
            tokens.append(token)
    return tokens


# ---------------------------------------------------------------------------
# BM25 (keyword search)
# ---------------------------------------------------------------------------
class BM25:
    """Okapi BM25 (Robertson & Zaragoza, 2009), the standard keyword ranking.

    k1 = how fast repeated words stop adding score; b = how much long chunks are
    penalised. 1.5 and 0.75 are the usual defaults.
    """

    def __init__(self, documents, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.doc_tokens = [Counter(tokenize(doc)) for doc in documents]
        self.doc_lengths = np.array([sum(counts.values()) for counts in self.doc_tokens])
        self.average_length = self.doc_lengths.mean()
        document_frequency = Counter(word for counts in self.doc_tokens for word in counts)
        total = len(documents)
        # Rare words get a high weight (np.random.normal), common words almost none (the).
        self.idf = {
            word: math.log(1 + (total - count + 0.5) / (count + 0.5))
            for word, count in document_frequency.items()
        }

    def scores(self, query):
        result = np.zeros(len(self.doc_tokens))
        for word in set(tokenize(query)):
            if word not in self.idf:
                continue
            for index, counts in enumerate(self.doc_tokens):
                frequency = counts.get(word, 0)
                if frequency:
                    length_penalty = 1 - self.b + self.b * self.doc_lengths[index] / self.average_length
                    result[index] += self.idf[word] * frequency * (self.k1 + 1) / (frequency + self.k1 * length_penalty)
        return result


# ---------------------------------------------------------------------------
# Dense (embedding) search
# ---------------------------------------------------------------------------
def load_embedding_model():
    # Imported here so BM25-only use doesn't need to load the model.
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=EMBEDDING_MODEL, cache_dir=str(MODEL_CACHE))


def embeddings_file(code):
    """One vector file per text variant, e.g. data/embeddings-all.npy."""
    return TUTOR_DIR / "data" / f"embeddings-{code}.npy"


def build_embeddings(chunks, code="all"):
    """Embed every chunk once and save the vectors next to chunks.json.

    Note: the model reads at most 512 tokens, so the tail of the longest chunks
    (up to ~830 words) is not embedded. BM25 still sees the whole chunk.
    """
    model = load_embedding_model()
    vectors = np.array(list(model.passage_embed([search_text(chunk, code) for chunk in chunks])))
    # Unit length, so a dot product equals cosine similarity.
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    np.save(embeddings_file(code), vectors.astype(np.float32))
    return vectors


class DenseIndex:
    def __init__(self, vectors):
        self.vectors = vectors
        self.model = load_embedding_model()

    def scores(self, query):
        # query_embed adds bge's search instruction; passages were embedded without it.
        query_vector = np.array(list(self.model.query_embed([query])))[0]
        query_vector /= np.linalg.norm(query_vector)
        return self.vectors @ query_vector   # cosine similarity with every chunk, ~1 ms


# ---------------------------------------------------------------------------
# Hybrid + boost
# ---------------------------------------------------------------------------
def ranks_from_scores(scores):
    """Position of each chunk in the ranking (0 = best)."""
    order = np.argsort(-scores, kind="stable")
    ranks = np.empty(len(scores), dtype=int)
    ranks[order] = np.arange(len(scores))
    return ranks


def lesson_sort_key(lesson_id):
    return tuple(int(part) for part in lesson_id.split("."))


class Retriever:
    """All four setups over one set of chunks, with the day-6 settings:

    bm25_code / dense_code  which code blocks each index sees (see search_text)
    type_weights            multiply a chunk's hybrid score by its section type's weight,
                            e.g. {"summary": 0.7}: summaries repeat every keyword of the
                            lesson and were beating the real answer (FAILURES.md)
    """

    def __init__(self, chunks, vectors, bm25_code="all", type_weights=None):
        self.chunks = chunks
        self.bm25 = BM25([search_text(chunk, bm25_code) for chunk in chunks])
        self.dense = DenseIndex(vectors)
        self.chunk_lessons = np.array([chunk["lesson_id"] for chunk in chunks])
        self.type_weights = np.array([(type_weights or {}).get(chunk["section_type"], 1.0) for chunk in chunks])
        # Curriculum neighbours = the previous and next SHIPPED lesson in numeric order,
        # which is the same order as subtopics.ts. A lesson's neighbour usually shares
        # its topic (2.1.3 circles next to 2.1.4 stars).
        lessons = sorted(set(self.chunk_lessons), key=lesson_sort_key)
        self.neighbours = {
            lesson: {lessons[i - 1] if i > 0 else None, lessons[i + 1] if i + 1 < len(lessons) else None} - {None}
            for i, lesson in enumerate(lessons)
        }

    def lesson_relation(self, asked_on):
        """1.0 for chunks on the learner's page, 0.5 for neighbour lessons, else 0."""
        relation = (self.chunk_lessons == asked_on).astype(float)
        for neighbour in self.neighbours.get(asked_on, ()):
            relation[self.chunk_lessons == neighbour] = 0.5
        return relation

    def search(self, query, setup="hybrid", asked_on=None, boost=0.0, top_k=5):
        """Return ([(chunk_index, score), ...] best first, best dense cosine).

        The best cosine is what the day-5 harness tested for 'nothing relevant found'
        (it does not work; see follow-ups #8).
        """
        dense_scores = self.dense.scores(query)
        best_cosine = float(dense_scores.max())
        if setup == "bm25":
            final = self.bm25.scores(query)
        elif setup == "dense":
            final = dense_scores
        elif setup == "hybrid":
            # RRF (flashcard 5): BM25 scores ~0-15 and cosine ~0-1 aren't comparable,
            # so only each chunk's rank in the two lists counts.
            final = (1 / (RRF_K + 1 + ranks_from_scores(self.bm25.scores(query)))
                     + 1 / (RRF_K + 1 + ranks_from_scores(dense_scores)))
            final = final * self.type_weights
            if boost and asked_on:
                # A bonus, not a filter (teach-first part 4): other lessons can still win.
                final = final + boost * self.lesson_relation(asked_on)
        else:
            raise ValueError(f"unknown setup {setup!r}")
        best = np.argsort(-final, kind="stable")[:top_k]
        return [(int(index), float(final[index])) for index in best], best_cosine


# The settings chosen on the dev half in Milestone 1 (see evals/results/experiments.md).
# Text and section-weight changes stayed within +-1 dev question (noise), so the simpler
# settings are kept; only the boost moved (0.005 -> 0.01, best on-page/off-page balance).
DEFAULT_SETTINGS = {"bm25_code": "all", "dense_code": "all", "type_weights": None, "boost": 0.01}


def load_retriever(bm25_code=None, dense_code=None, type_weights=None, use_defaults=True):
    settings = dict(DEFAULT_SETTINGS) if use_defaults else {}
    for key, value in (("bm25_code", bm25_code), ("dense_code", dense_code), ("type_weights", type_weights)):
        if value is not None:
            settings[key] = value
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    vector_file = embeddings_file(settings.get("dense_code", "all"))
    if not vector_file.exists():
        sys.exit(f"No {vector_file.name}: run  ai-tutor/.venv/Scripts/python ai-tutor/retrieval.py --build")
    vectors = np.load(vector_file)
    if len(vectors) != len(chunks):
        # The silent failure from flashcard 4: chunks changed but the vectors did not.
        sys.exit(f"{vector_file.name} is out of date with chunks.json: rebuild with --build")
    return Retriever(chunks, vectors, settings.get("bm25_code", "all"), settings.get("type_weights"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:2] == ["--build"]:
        # --build [code variant], e.g. --build none for prose-only embeddings
        code = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SETTINGS["dense_code"]
        chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
        vectors = build_embeddings(chunks, code)
        print(f"embedded {len(vectors)} chunks ({code}) with {EMBEDDING_MODEL} -> {embeddings_file(code).name}")
        return
    if not sys.argv[1:]:
        sys.exit(__doc__)
    query = sys.argv[1]
    asked_on = sys.argv[2] if len(sys.argv) > 2 else None
    retriever = load_retriever()
    for setup, boost in [("bm25", 0), ("dense", 0), ("hybrid", 0), ("hybrid", DEFAULT_SETTINGS["boost"])]:
        label = setup + (" + boost" if boost else "")
        results, best_cosine = retriever.search(query, setup, asked_on, boost, top_k=3)
        print(f"\n{label}")
        for index, score in results:
            chunk = retriever.chunks[index]
            print(f"  {score:7.4f}  {chunk['id']}")


if __name__ == "__main__":
    main()
