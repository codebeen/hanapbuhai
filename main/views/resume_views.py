from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

# Create your views here.
def generate_resume(request):
    return render(request, 'resume/resume-builder.html')

@csrf_exempt
def generate_summary(request):
    if request.method == "POST":
        data = json.loads(request.body)
        education = data.get("education", "")
        experience = data.get("experience", "")
        skills = data.get("skills", "")

        prompt = (
            f"Write a short, compelling 3-sentence professional summary for a resume "
            f"based on this education: {education}; experience: {experience}; skills: {skills}. "
            f"Keep it concise, professional, and impressive."
        )

        # Use Gemini model
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        summary = response.text.strip()

        return JsonResponse({"summary": summary})

    return JsonResponse({"error": "Invalid request"}, status=400)