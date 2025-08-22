"""
Celery tasks for processing large files of Persian text.

If Celery and Redis are configured, this task allows the service to process
large input files asynchronously, line by line, and output a JSON file
containing the results for each line. The resulting file name is derived
from the input file name by appending ``_analysis.json`` before the file
extension.

If you prefer to run the analysis synchronously, remove this module and
adjust the API view accordingly.
"""

from __future__ import annotations

import json
import os
from celery import shared_task

from .pipelines import analyse_text


@shared_task
def analyze_file_task(path: str) -> dict[str, object]:
    """
    Analyse each line of a text file and write the results to a JSON file.

    This task reads the given UTF‑8 encoded file line by line, skipping
    blank lines, and for each non‑empty line invokes ``analyse_text`` to
    obtain the normalised text, sentiment, and entities. It writes the
    collection of results to a new JSON file in the same directory as
    ``path``, with ``_analysis.json`` appended to the base file name.

    :param path: Absolute or relative path to the input text file.
    :return: A dictionary summarising the output file and number of lines
             processed.
    :rtype: dict[str, object]
    """
    results: list[dict[str, object]] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            analysis = analyse_text(line)
            results.append({'input': line, 'analysis': analysis})

    # Construct output file path by inserting '_analysis' before extension
    root, ext = os.path.splitext(path)
    out_path = f"{root}_analysis.json"
    with open(out_path, 'w', encoding='utf-8') as fout:
        json.dump(results, fout, ensure_ascii=False, indent=2)
    return {'result_file': out_path, 'count': len(results)}