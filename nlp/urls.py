"""
URL configuration for the NLP API endpoints.

Defines routes for analysing text and checking the status of background jobs.
These URLs are included from the project’s root URL configuration under
the ``/api/`` prefix.
"""

from django.urls import path
from .views import AnalyzeAPIView, JobStatusAPIView, AnswerAPIView


urlpatterns = [
    path('analyze/', AnalyzeAPIView.as_view(), name='nlp-analyze'),
    path('jobs/<str:task_id>/', JobStatusAPIView.as_view(), name='nlp-job-status'),
    # New endpoint for question answering
    path('answer/', AnswerAPIView.as_view(), name='nlp-answer'),
]