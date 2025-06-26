from datetime import datetime
import json
import os
import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import requests
from django.conf import settings
from django.core.paginator import Paginator
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import tempfile
from docx import Document

# Create your views here.
def homepage(request):
    file_path = os.path.join(settings.BASE_DIR, 'ph-jobs.json')
    with open(file_path, encoding='utf-8') as f:
        jobs = json.load(f)

    print(f"Jobs loaded: {len(jobs)}")

    for job in jobs:
        date_posted_str = job.get('date_posted')
        if date_posted_str:
            try:
                job['date_posted'] = datetime.fromisoformat(date_posted_str)
            except ValueError:
                job['date_posted'] = None
        else:
            job['date_posted'] = None

    # ✅ Pick 4 random jobs
    random_jobs = random.sample(jobs, k=4) if len(jobs) >= 4 else jobs

    return render(request, 'jobs/homepage.html', {
        'random_jobs': random_jobs
    })


def list_jobs(request):
    # Load jobs from the JSON file
    file_path = os.path.join(settings.BASE_DIR, 'ph-jobs.json')
    with open(file_path, encoding='utf-8') as f:
        jobs = json.load(f)

    print(f"Jobs loaded: {len(jobs)}")

    for job in jobs:
        # Example: parse 'date_posted'
        date_posted_str = job.get('date_posted')
        if date_posted_str:
            try:
                job['date_posted'] = datetime.fromisoformat(date_posted_str)
            except ValueError:
                job['date_posted'] = None
        else:
            job['date_posted'] = None

    # Set up pagination — 10 jobs per page
    paginator = Paginator(jobs, 10)  # 10 per page

    # Get current page number from URL query parameter ?page=...
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass only the current page of jobs to template
    return render(request, 'jobs/job-list.html', {
        'page_obj': page_obj,
    })


def filtered_jobs(request):
    # Load jobs from JSON file
    file_path = os.path.join(settings.BASE_DIR, 'ph-jobs.json')
    with open(file_path, encoding='utf-8') as f:
        jobs = json.load(f)

    print(f"Jobs loaded: {len(jobs)}")

    # Parse date_posted for each job
    for job in jobs:
        date_posted_str = job.get('date_posted')
        try:
            job['date_posted'] = datetime.fromisoformat(date_posted_str) if date_posted_str else None
        except ValueError:
            job['date_posted'] = None

    # Get filters
    keyword = request.GET.get('keyword', '').strip().lower()
    location = request.GET.get('location', '').strip().lower()
    employment_type = request.GET.get('employment_type', '').strip().lower()

    print(f"Filters: keyword={keyword}, location={location}, employment_type={employment_type}")

    filtered_jobs = []

    for job in jobs:
        title = (job.get('title') or '').lower()
        org = (job.get('organization') or '').lower()
        locations = ', '.join(job.get('locations_derived') or []).lower()
        types = [t.lower() for t in (job.get('employment_type') or [])]

        # Check each filter
        matches_keyword = keyword and (
            keyword in title or
            keyword in org or
            keyword in locations
        )

        matches_location = location and location in locations

        matches_type = employment_type and any(employment_type in t for t in types)

        # Include job if ANY matches (not all)
        if matches_keyword or matches_location or matches_type:
            filtered_jobs.append(job)

    # If no filters, include all jobs
    if not any([keyword, location, employment_type]):
        filtered_jobs = jobs

    print(f"Filtered jobs: {len(filtered_jobs)}")

    # Paginate — 10 per page
    paginator = Paginator(filtered_jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/job-list.html', {
        'page_obj': page_obj,
    })


def extract_resume_text(request):
    if request.method == 'GET':
        # Get fields from form POST
        keyword = request.GET.get('keyword', '').strip().lower()
        location = request.GET.get('location', '').strip().lower()
        employment_type = request.GET.get('employment_type', '').strip().lower()

        uploaded_file = request.FILES.get('resume')
        extracted_text = ""

        # If resume uploaded, extract text
        if uploaded_file:
            file_name = uploaded_file.name.lower()
            if file_name.endswith('.pdf'):
                pdf_bytes = uploaded_file.read()
                images = convert_from_bytes(pdf_bytes)
                text_chunks = [pytesseract.image_to_string(img) for img in images]
                extracted_text = "\n".join(text_chunks)
            elif file_name.endswith(('.jpg', '.jpeg', '.png')):
                img = Image.open(uploaded_file)
                extracted_text = pytesseract.image_to_string(img)
            elif file_name.endswith(('.doc', '.docx')):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_doc:
                    for chunk in uploaded_file.chunks():
                        temp_doc.write(chunk)
                    temp_doc.flush()
                    doc = Document(temp_doc.name)
                    extracted_text = "\n".join([p.text for p in doc.paragraphs])

        # If keyword empty, fallback to extracted text
        if not keyword and extracted_text:
            keyword = extracted_text.strip().lower()

        # Load jobs from JSON
        file_path = os.path.join(settings.BASE_DIR, 'ph-jobs.json')
        with open(file_path, encoding='utf-8') as f:
            jobs = json.load(f)

        # Parse date_posted
        for job in jobs:
            date_posted_str = job.get('date_posted')
            if date_posted_str:
                try:
                    job['date_posted'] = datetime.fromisoformat(date_posted_str)
                except ValueError:
                    job['date_posted'] = None
            else:
                job['date_posted'] = None

        #  Filter: match ANY field
        filtered_jobs = []
        for job in jobs:
            title = job.get('title', '').lower()
            org = job.get('organization', '').lower()
            locations = ", ".join(job.get('locations_derived') or []).lower()
            types = [t.lower() for t in (job.get('employment_type') or [])]

            matches_keyword = keyword and (
                keyword in title or
                keyword in org or
                keyword in locations
            )
            matches_location = location and location in locations
            matches_type = employment_type and employment_type in types

            if matches_keyword or matches_location or matches_type:
                filtered_jobs.append(job)

        #  Paginate: preserve page for GET
        paginator = Paginator(filtered_jobs, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'jobs/job-list.html', {
            'page_obj': page_obj,
        })