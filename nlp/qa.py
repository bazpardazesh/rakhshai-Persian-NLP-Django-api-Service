"""
Question answering utilities for Persian history questions.

This module provides a simple question‑answering mechanism geared toward
historical questions about ancient Iran.  It first attempts to match the
incoming question against a curated list of frequently asked questions
about the Achaemenid period.  When no satisfactory match is found, a
fallback routine queries the Persian edition of Wikipedia to retrieve a
brief summary related to the question.  This approach ensures that the
service can respond quickly to known prompts while still offering a
best‑effort answer for novel queries by leveraging publicly available
information.

To add or modify question–answer pairs, edit the ``qa_data.json`` file
located in the same package.  Each entry must contain a ``question``
string and its corresponding ``answer``.

**Dependencies**: This module uses the following optional libraries:

* ``hazm`` – for normalising and tokenising Persian text.  If it is not
  available, a basic whitespace tokenizer is used instead.
* ``wikipedia`` – for retrieving summaries from Persian Wikipedia.  If
  unavailable or if network requests fail, the fallback will return
  ``None``.  Install via ``pip install wikipedia``.
* ``requests`` – as an alternative to ``wikipedia`` for fetching
  summaries via the Wikimedia REST API.  Most Python distributions
  include ``requests`` by default.

Note that Internet access is required for the fallback search to work.
If the question cannot be answered locally and no external network
connection is available, the caller will receive a generic
``"جواب یافت نشد"`` message.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Attempt to import optional dependencies.  These imports are not
# mandatory; the code falls back to basic functionality when they are
# unavailable.
try:
    from hazm import Normalizer, word_tokenize
    _normalizer = Normalizer()
    def _normalize(text: str) -> str:
        """Normalise Persian text using Hazm if available."""
        return _normalizer.normalize(text)
    def _tokenize(text: str) -> List[str]:
        return word_tokenize(text)
except Exception:
    # Provide simple normalise/tokenise functions if hazm is missing.
    def _normalize(text: str) -> str:
        return text.strip()
    def _tokenize(text: str) -> List[str]:
        return text.split()

try:
    import wikipedia
    _have_wikipedia = True
except Exception:
    wikipedia = None  # type: ignore
    _have_wikipedia = False

try:
    import requests
    _have_requests = True
except Exception:
    requests = None  # type: ignore
    _have_requests = False

# Path to the bundled QA dataset
QA_FILE = Path(__file__).resolve().parent / "qa_data.json"

def _load_dataset() -> List[Dict[str, str]]:
    """Load the question–answer pairs from the JSON file.  The dataset is
    cached on first load to avoid repeated disk access."""
    if not hasattr(_load_dataset, "_cache"):
        try:
            with open(QA_FILE, "r", encoding="utf-8") as f:
                _load_dataset._cache = json.load(f)
        except Exception:
            _load_dataset._cache = []
    return list(_load_dataset._cache)  # type: ignore


def _similarity(tokens1: List[str], tokens2: List[str]) -> float:
    """Compute a simple Jaccard similarity between two token lists."""
    if not tokens1 or not tokens2:
        return 0.0
    set1, set2 = set(tokens1), set(tokens2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)


def _match_local(question: str, threshold: float = 0.2) -> Optional[str]:
    """
    Attempt to find an answer to the question from the local dataset.

    The function normalises and tokenises the incoming question and
    compares it against each stored question using a simple Jaccard
    similarity score.  The entry with the highest score above the
    threshold is returned.

    :param question: Input question string (assumed to be Persian).
    :param threshold: Minimum similarity required to accept a match.
    :returns: The corresponding answer string, or ``None`` if no
              satisfactory match is found.
    """
    q_norm = _normalize(question)
    q_tokens = _tokenize(q_norm)
    best_score = 0.0
    best_answer: Optional[str] = None
    for entry in _load_dataset():
        entry_q_norm = _normalize(entry.get("question", ""))
        entry_tokens = _tokenize(entry_q_norm)
        score = _similarity(q_tokens, entry_tokens)
        if score > best_score and score >= threshold:
            best_score = score
            best_answer = entry.get("answer")
    return best_answer


def _search_wikipedia(query: str, sentences: int = 2) -> Optional[str]:
    """
    Search the Persian Wikipedia for a brief summary related to the query.

    This function uses the ``wikipedia`` library when available to
    perform the search and retrieve a summary.  If the library is not
    installed or fails, a fallback using the Wikimedia REST API is
    attempted.  In the latter case, only the first matching page is
    returned.

    :param query: The user’s question or topic to look up.
    :param sentences: Desired number of sentences in the summary.
    :returns: A summary string if successful, otherwise ``None``.
    """
    # Attempt using the wikipedia library
    if _have_wikipedia:
        try:
            wikipedia.set_lang("fa")
            # Search for relevant pages; use the top result
            results = wikipedia.search(query)
            if results:
                page_title = results[0]
                summary = wikipedia.summary(page_title, sentences=sentences)
                return summary
        except Exception:
            pass
    # Fallback to REST API if requests is available
    if _have_requests:
        try:
            from urllib.parse import quote
            endpoint = "https://fa.wikipedia.org/api/rest_v1/page/summary/"
            # encode the query as a page title; this may or may not exist
            url = endpoint + quote(query)
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # Extract up to the desired number of sentences
                extract = data.get("extract")
                if extract:
                    sentences_split = extract.split(".")
                    summary = ".".join(sentences_split[:sentences]).strip()
                    if not summary.endswith("."):
                        summary += "."
                    return summary
        except Exception:
            pass
    return None


def answer_question(question: str) -> str:
    """
    Provide an answer to a Persian question about ancient Iranian history.

    The function first attempts to match the question against the local
    dataset of frequently asked questions.  If no answer is found, it
    queries Persian Wikipedia for a short summary.  If both methods fail,
    a generic message is returned indicating that no answer was found.

    :param question: The user’s question.
    :returns: An answer string.
    """
    # Try to answer from the curated dataset
    answer = _match_local(question)
    if answer:
        return answer
    # Fallback to internet search (requires external connectivity)
    summary = _search_wikipedia(question)
    if summary:
        return summary
    # Final fallback
    return "جواب یافت نشد."
