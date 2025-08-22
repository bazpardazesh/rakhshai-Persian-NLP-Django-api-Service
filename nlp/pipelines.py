"""
Core analysis pipelines for Persian text.

This module defines helper functions to normalise and analyse Persian text
using the Hazm library and pre‑trained Transformer models for sentiment
analysis and named entity recognition (NER). It uses the Hugging Face
``transformers`` library to load models via the pipeline API. Results include
both sentiment labels and detected entities with spans.

The functions herein lazily load the models on first use to avoid
overhead during startup. The device (CPU or GPU) is chosen automatically
based on PyTorch CUDA availability.

**Copyright**: The implementation is the property of ``rakhshai`` and
distributed as part of a beta release.
"""

from __future__ import annotations

# Attempt to import the Hazm normaliser.  If it is not available,
# provide a simple fallback that performs no normalisation.
try:
    from hazm import Normalizer  # type: ignore
    normalizer = Normalizer()
except Exception:
    normalizer = None  # type: ignore

# -----------------------------------------------------------------------------
# Preprocessing: normaliser
# -----------------------------------------------------------------------------
if normalizer is None:
    # Define a basic normalise function when Hazm is unavailable.  This
    # fallback simply strips the string; it does not perform any
    # morphological normalisation.
    def _basic_normalize(text: str) -> str:
        return text.strip()
    # Expose a minimal interface with a ``normalize`` method
    class _BasicNormalizer:
        def normalize(self, text: str) -> str:
            return _basic_normalize(text)
    normalizer = _BasicNormalizer()  # type: ignore

#
# Simple lexicon‑based sentiment analysis and dictionary‑driven NER
#
# The previous version of this module relied on heavy Transformer models from
# HooshvareLab for both sentiment analysis and named entity recognition (NER).
# Those models are no longer used in this project.  Instead, the
# implementation below provides lightweight, offline alternatives based on
# manually curated word lists.  While these methods are simplistic and not
# state of the art, they remove the dependency on large pre‑trained models and
# still offer useful functionality for demonstration and educational purposes.

# Holders for the analysis functions (lazy initialisation).  The variables
# `_sentiment_pipe` and `_ner_pipe` previously referenced Hugging Face
# pipelines; they are now callables that return analysis results when
# invoked with a string.  They are initialised on first access via
# ``get_pipelines``.
_sentiment_pipe = None  # type: ignore[assignment]
_ner_pipe = None  # type: ignore[assignment]


def _load_sentiment() -> callable:
    """Initialise and return the simple sentiment analysis function.

    The returned function takes a normalised Persian string and produces
    a list with a single dictionary containing a ``label`` (``POSITIVE``,
    ``NEGATIVE`` or ``NEUTRAL``) and a ``score`` between 0 and 1.  The score
    reflects the relative strength of the sentiment based on the counts of
    positive and negative keywords.  A lack of matches yields a neutral
    sentiment with full confidence.

    :returns: Callable for sentiment analysis.
    """
    # Define a small set of positive and negative sentiment words.  These
    # lists are by no means comprehensive; feel free to extend them as
    # needed.  Words should be normalised before matching.
    positive_words = {
        'خوب', 'عالی', 'مثبت', 'زیبا', 'دوست‌داشتنی', 'موفق', 'فرخنده',
        'شاد', 'خوش', 'بهتر', 'دلنشین', 'قدرتمند', 'پیروزمند', 'شاداب',
    }
    negative_words = {
        'بد', 'منفی', 'زشت', 'نفرت', 'غمگین', 'شکست', 'تلخ', 'خطرناک',
        'ناامید', 'بدتر', 'بی‌رحم', 'ضعیف', 'تراژدی', 'اندوه',
    }

    def analyse_sentiment(text: str) -> list[dict[str, object]]:
        """Compute a simple sentiment score for the given text.

        :param text: Normalised Persian text.
        :returns: A list containing one dictionary with ``label`` and ``score``.
        """
        # Count occurrences of positive and negative words by substring match.
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        total = pos_count + neg_count
        if total == 0:
            # No sentiment words found; return neutral with full confidence.
            return [{'label': 'NEUTRAL', 'score': 1.0}]
        diff = pos_count - neg_count
        # Score is the absolute difference divided by total; ensures a value
        # between 0 and 1.  The larger the difference, the stronger the
        # confidence.  A difference of zero would have been caught above.
        score = abs(diff) / total
        label = 'POSITIVE' if diff > 0 else 'NEGATIVE'
        return [{'label': label, 'score': float(score)}]

    return analyse_sentiment


def _load_ner() -> callable:
    """Initialise and return the simple NER function.

    The returned function takes a normalised Persian string and returns a
    list of entity dictionaries with keys ``word`` (the matched substring),
    ``entity_group`` (entity label), ``score`` (confidence score), ``start``
    and ``end`` (character offsets).  The implementation uses fixed lists
    of person names, organisations and locations.  All matches are
    case-sensitive and do not handle overlapping entities gracefully; longer
    names are matched first.

    :returns: Callable for named entity recognition.
    """
    # Define some sample entities for demonstration.  These lists are not
    # exhaustive; they simply illustrate how a dictionary-based approach can
    # identify well‑known names and terms.  You can expand these lists to
    # improve coverage for your specific domain.
    entity_list: list[tuple[str, str]] = [
        # Persons
        ('کوروش بزرگ', 'PER'),
        ('کوروش', 'PER'),
        ('داریوش', 'PER'),
        ('داریوش بزرگ', 'PER'),
        ('خشایارشا', 'PER'),
        ('کمبوجیه', 'PER'),
        ('اردشیر', 'PER'),
        ('اسکندر مقدونی', 'PER'),
        ('اسکندر', 'PER'),
        # Organisations / states
        ('امپراتوری هخامنشی', 'ORG'),
        ('شاهنشاهی هخامنشی', 'ORG'),
        ('امپراتوری ساسانی', 'ORG'),
        ('شاهنشاهی ساسانی', 'ORG'),
        # Locations
        ('ایران', 'LOC'),
        ('پارس', 'LOC'),
        ('یونان', 'LOC'),
        ('مصر', 'LOC'),
        ('بابل', 'LOC'),
    ]
    # Sort by length descending to match longer names first.
    entity_list.sort(key=lambda x: len(x[0]), reverse=True)

    def analyse_entities(text: str) -> list[dict[str, object]]:
        """Detect entities in the given text using a simple lookup table.

        The function scans the normalised text for occurrences of the names
        defined in ``entity_list``.  Longer names are matched first to
        minimise overlapping matches.  If a candidate match overlaps with
        previously detected entities, it is skipped to avoid duplicate
        detection.

        :param text: Normalised Persian text.
        :returns: A list of detected entities with spans and labels.
        """
        entities: list[dict[str, object]] = []
        occupied: list[tuple[int, int]] = []  # keep track of used spans
        for name, label in entity_list:
            start_search = 0
            while True:
                idx = text.find(name, start_search)
                if idx == -1:
                    break
                end_idx = idx + len(name)
                # Check for overlap with existing entities
                overlap = False
                for s, e in occupied:
                    if not (end_idx <= s or idx >= e):
                        overlap = True
                        break
                if not overlap:
                    entities.append({
                        'word': name,
                        'entity_group': label,
                        'score': 1.0,
                        'start': idx,
                        'end': end_idx,
                    })
                    occupied.append((idx, end_idx))
                # Continue searching after the current match
                start_search = end_idx
        return entities

    return analyse_entities


def get_pipelines() -> tuple[callable, callable]:
    """
    Lazy loader for the sentiment and NER functions.

    Returns a tuple containing the sentiment analysis callable followed by
    the named entity recognition callable.  These functions are created
    lazily on first access to avoid unnecessary setup during module import.

    :return: (sentiment analyser, NER analyser)
    :rtype: tuple[callable, callable]
    """
    global _sentiment_pipe, _ner_pipe
    if _sentiment_pipe is None:
        _sentiment_pipe = _load_sentiment()
    if _ner_pipe is None:
        _ner_pipe = _load_ner()
    return _sentiment_pipe, _ner_pipe


def analyse_text(text: str) -> dict[str, object]:
    """
    Analyse a Persian text string by normalising it, computing sentiment and
    extracting named entities.

    This function orchestrates the three stages of processing:

    * **Normalisation** – performed using the Hazm normaliser.  The input
      string is converted to a canonical form (e.g. unifying characters,
      fixing spacing).
    * **Sentiment analysis** – a lightweight rule‑based approach that
      counts occurrences of positive and negative words in the normalised
      text.  It outputs a label (``POSITIVE``, ``NEGATIVE`` or ``NEUTRAL``)
      along with a simple confidence score.  No external models are
      required.
    * **Named entity recognition** – implemented via a dictionary lookup
      using curated lists of historical Persian names, empires and
      locations.  Each match produces an entity with its span and a
      heuristic confidence score of 1.0.

    The returned dictionary contains three keys:

    ``normalized`` – the normalised text produced by Hazm.

    ``sentiment`` – a dictionary with two keys, ``label`` and ``score``,
    representing the sentiment label and its confidence.

    ``entities`` – a list of detected entities; each entity is itself a
    dictionary containing ``text`` (the matched substring), ``label`` (the
    entity type), ``score`` (heuristic confidence), ``start`` and ``end``
    offsets within the original normalised text.

    :param text: Input Persian text to analyse.
    :return: Analysis results as a dictionary.
    :rtype: dict[str, object]
    """
    s_pipe, n_pipe = get_pipelines()
    # Normalise the text (e.g. convert half spaces, fix numbers, etc.)
    text_norm = normalizer.normalize(text)
    # Sentiment analysis (returns list of predictions; pick first entry)
    s = s_pipe(text_norm)[0]
    # NER returns a list of entities with character spans
    ents_raw = n_pipe(text_norm)
    # Convert to simpler dicts for the API response
    entities: list[dict[str, object]] = [
        {
            'text': ent.get('word') or ent.get('entity_group'),
            'label': ent.get('entity_group'),
            'score': float(ent['score']),
            'start': int(ent['start']),
            'end': int(ent['end']),
        }
        for ent in ents_raw
    ]
    return {
        'normalized': text_norm,
        'sentiment': {
            'label': s['label'],
            'score': float(s['score']),
        },
        'entities': entities,
    }


# Backwards compatibility alias (British vs American spelling)
analyze_text = analyse_text