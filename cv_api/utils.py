import os
import re
import json
from pypdf import PdfReader


def extract_text_from_pdf(pdf_file):
    """Extracts all text from a PDF file-like object."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""


def parse_cv_with_gemini(text):
    """
    Uses the Gemini API to intelligently parse raw CV text into a structured JSON.
    Returns a dict matching our database models.
    """
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are a CV/Resume parser. Extract all information from the following CV text and return it as a valid JSON object.

Use EXACTLY this JSON structure. If any field is not found, use null or an empty array [].

{{
  "personal_details": {{
    "firstName": "",
    "lastName": "",
    "email": "",
    "phone": "",
    "address": "",
    "cityState": "",
    "country": "",
    "dateOfBirth": "",
    "placeOfBirth": "",
    "gender": "",
    "nationality": "",
    "linkedin": "",
    "github": ""
  }},
  "summary": "",
  "work_experiences": [
    {{
      "job_title": "",
      "employer": "",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD or null",
      "is_current": false,
      "city_state": "",
      "description": ["bullet 1", "bullet 2"]
    }}
  ],
  "education": [
    {{
      "school": "",
      "degree": "",
      "start_date": "",
      "end_date": "",
      "is_current": false,
      "city_state": "",
      "description": ""
    }}
  ],
  "skills": [
    {{
      "skill_name": "",
      "level": "Beginner | Intermediate | Advanced | Expert"
    }}
  ],
  "languages": [
    {{
      "language": "",
      "level": "Basic | Conversational | Fluent | Native"
    }}
  ],
  "certificates": [
    {{
      "title": "",
      "date": "",
      "description": ""
    }}
  ],
  "projects": [
    {{
      "title": "",
      "description": ["bullet 1"],
      "github_link": "",
      "live_link": "",
      "technologies": ""
    }}
  ],
  "qualities": [
    {{"quality": ""}}
  ],
  "references": [
    {{
      "name": "",
      "role": "",
      "company": "",
      "phone": "",
      "email": ""
    }}
  ]
}}

IMPORTANT:
- Return ONLY the raw JSON. No markdown, no code blocks, no extra text.
- For dates in work_experiences, use YYYY-MM-DD format. If only year is available, use YYYY-01-01. If it's a current job, set end_date to null and is_current to true.
- description in work_experiences and projects must be a JSON array of strings (bullet points).

CV TEXT:
---
{text}
---
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if Gemini wraps it anyway
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)

    return json.loads(raw)
