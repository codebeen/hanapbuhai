from django.urls import path

from main.views import jobs_views, resume_views

urlpatterns = [
    path('', jobs_views.homepage, name="homepage"),
    path('resume', resume_views.generate_resume, name="generate_resume"),
    path('generate-summary/', resume_views.generate_summary, name="generate_summary"),
    path('jobs/', jobs_views.list_jobs, name="list_jobs"),
    path('filtered-jobs/', jobs_views.filtered_jobs, name="filtered_jobs"),
    path('extract-resume-text/', jobs_views.extract_resume_text, name='extract_resume_text'),
]