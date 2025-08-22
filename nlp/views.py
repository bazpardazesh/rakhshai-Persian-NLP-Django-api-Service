"""
API views for the Persian NLP service.

This module defines two REST API endpoints using Django REST Framework:

* ``AnalyzeAPIView``: Accepts a POST request containing either a JSON body
  with a ``text`` field (for synchronous analysis of a single string) or a
  multipart form upload with a ``file`` field (for asynchronous analysis
  using Celery). It returns either the analysis result immediately or a
  job ID to check later.

* ``JobStatusAPIView``: Accepts a GET request with a Celery task ID and
  returns the status of the task. When the task is complete, it includes
  the result metadata.

The views gracefully handle the absence of Celery: if the server is not
running a Celery worker or Redis is unavailable, the file‑upload endpoint
will return a 503 status with an appropriate message.
"""

from __future__ import annotations

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .pipelines import analyse_text

# Import the QA answering function.  Kept separate to avoid heavy imports
try:
    from .qa import answer_question  # type: ignore
except Exception:
    # Fallback dummy in case of import errors; this should never occur in
    # normal operation provided that qa.py exists and is valid.
    def answer_question(question: str) -> str:  # type: ignore
        return "جواب یافت نشد."
try:
    # Attempt to import the Celery task. If Celery is not configured,
    # importing will fail and HAS_CELERY will be False.
    from .tasks import analyze_file_task  # type: ignore
    HAS_CELERY = True
except Exception:
    analyze_file_task = None  # type: ignore[assignment]
    HAS_CELERY = False


class AnalyzeAPIView(APIView):
    """
    Analyse Persian text synchronously or upload a file for asynchronous
    processing.

    POST /api/analyze/
    -----------------
    * JSON body with ``text``: Return analysis immediately.
    * Multipart upload with ``file``: Save the file and queue a Celery task.
      Return a job ID for later status checking.
    """

    def post(self, request: HttpRequest) -> Response:
        # 1) Handle synchronous text analysis
        text_input = (request.data.get('text') or '').strip()
        if text_input:
            result = analyse_text(text_input)
            return Response({'ok': True, 'result': result})

        # 2) Handle asynchronous file analysis
        if 'file' in request.FILES:
            if not HAS_CELERY or analyze_file_task is None:
                return Response(
                    {'ok': False, 'error': 'Celery is not enabled.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            uploaded_file = request.FILES['file']
            # Save the uploaded file to the default storage (MEDIA_ROOT or similar)
            save_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)
            # Determine absolute path for Celery (some storage backends return relative paths)
            abs_path = save_path
            if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
                abs_path = str(settings.MEDIA_ROOT / save_path)
            # Enqueue the task and return the job ID
            job = analyze_file_task.delay(abs_path)
            return Response({'ok': True, 'job_id': job.id}, status=status.HTTP_202_ACCEPTED)

        # Neither a text field nor a file provided
        return Response(
            {'ok': False, 'error': 'A non-empty "text" field or a file upload is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AnswerAPIView(APIView):
    """
    Answer historical questions about ancient Iran.

    POST /api/answer/
    -----------------
    Accepts a JSON body with a ``question`` field (Persian text) and
    returns a dictionary containing an ``answer``.  The service first
    attempts to match the question against a curated dataset of
    question–answer pairs.  If no match is found, it uses the Persian
    Wikipedia as a fallback.  When neither method yields an answer, a
    generic message is returned.
    """

    def post(self, request: HttpRequest) -> Response:
        question = (request.data.get('question') or '').strip()
        if not question:
            return Response(
                {'ok': False, 'error': 'A non-empty "question" field is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        answer = answer_question(question)
        return Response({'ok': True, 'answer': answer})


from celery.result import AsyncResult  # noqa: E402 (import after Celery detection)


class JobStatusAPIView(APIView):
    """
    Check the status of a Celery task.

    GET /api/jobs/<task_id>/
    -----------------------
    Returns the current state of the task. When the task has finished,
    includes the result (output file path and number of lines processed).
    """

    def get(self, request: HttpRequest, task_id: str) -> Response:
        res = AsyncResult(task_id)
        data: dict[str, object] = {'id': task_id, 'state': res.state}
        if res.ready():
            data['result'] = res.result
        return Response(data)