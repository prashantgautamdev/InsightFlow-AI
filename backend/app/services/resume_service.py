"""
Resume Analyzer service.

1. Extracts raw text from the uploaded PDF.
2. Uses regex/keyword heuristics to pull skills, education, experience.
3. Calls the configured AI provider to produce ATS score, skill-gap
   analysis, career suggestions, and a learning roadmap.
"""
import re
from typing import Any, Dict, List

import pdfplumber

from app.services.ai_provider import ai_complete_json

# A reasonably broad skill keyword bank used for fast regex-based extraction
# (kept separate from the AI call so the feature still partially works
# even if the AI provider is unavailable).
SKILL_BANK = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "sql",
    "r", "scala", "react", "next.js", "vue", "angular", "node.js", "fastapi", "django",
    "flask", "spring boot", "express", "tailwind css", "html", "css",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost",
    "machine learning", "deep learning", "nlp", "computer vision", "data analysis",
    "data visualization", "power bi", "tableau", "excel", "statistics",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "jenkins",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka", "spark",
    "hadoop", "airflow", "git", "rest api", "graphql", "microservices", "linux",
]

EDUCATION_PATTERN = re.compile(
    r"(bachelor|master|b\.?\s?tech|m\.?\s?tech|b\.?sc|m\.?sc|phd|mba|b\.?e\.?|m\.?e\.?)"
    r"[^\n]{0,80}",
    re.IGNORECASE,
)

EXPERIENCE_HEADER_PATTERN = re.compile(
    r"(\d{1,2}\+?\s*years?)\s*(of)?\s*experience", re.IGNORECASE
)


def extract_text_from_pdf(file_path: str) -> str:
    text_chunks: List[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def extract_skills(text: str) -> List[str]:
    lower = text.lower()
    found = {skill for skill in SKILL_BANK if skill in lower}
    return sorted(found)


def extract_education(text: str) -> List[Dict[str, Any]]:
    matches = EDUCATION_PATTERN.findall(text)
    seen = []
    for m in EDUCATION_PATTERN.finditer(text):
        snippet = m.group(0).strip()
        if snippet.lower() not in [s.lower() for s in seen]:
            seen.append(snippet)
    return [{"raw": s} for s in seen[:5]]


def extract_experience_years(text: str) -> float:
    match = EXPERIENCE_HEADER_PATTERN.search(text)
    if match:
        num = re.search(r"\d{1,2}", match.group(0))
        if num:
            return float(num.group(0))
    return 0.0


def compute_ats_score(text: str, found_skills: List[str], target_role: str | None) -> float:
    """Lightweight heuristic ATS score (0-100) used as a fallback / sanity check
    alongside the AI-generated score."""
    score = 0.0
    score += min(len(found_skills), 15) * 3            # up to 45 pts for skill breadth
    score += 15 if re.search(r"\b(experience|work history)\b", text, re.I) else 0
    score += 15 if re.search(r"\b(education|degree)\b", text, re.I) else 0
    score += 10 if re.search(r"\b(project|projects)\b", text, re.I) else 0
    score += 10 if re.search(r"\b(certification|certified)\b", text, re.I) else 0
    score += 5 if len(text.split()) > 250 else 0
    return round(min(score, 100.0), 1)


def analyze_resume_with_ai(
    resume_text: str,
    found_skills: List[str],
    target_role: str | None,
) -> Dict[str, Any]:
    """
    Single AI call that returns ATS score, missing skills, skill-gap
    analysis, career suggestions, and a roadmap, all as structured JSON.
    Falls back to a deterministic heuristic result if the AI call fails.
    """
    fallback = {
        "ats_score": compute_ats_score(resume_text, found_skills, target_role),
        "missing_skills": [],
        "skill_gap_analysis": {"strengths": found_skills[:8], "gaps": []},
        "career_suggestions": [
            {"role": "Data Analyst", "fit_reason": "Based on detected analytical skills."}
        ],
        "roadmap": {"next_3_months": [], "next_6_months": [], "next_12_months": []},
    }

    system = (
        "You are a senior technical recruiter and career coach specializing in "
        "data science, AI, and software engineering roles. You analyze resumes "
        "and return ONLY structured JSON."
    )
    prompt = f"""
Analyze this resume text and the target role: "{target_role or 'Data Scientist / AI Engineer'}".

Resume text:
\"\"\"{resume_text[:6000]}\"\"\"

Detected skills via keyword scan: {found_skills}

Return JSON with EXACTLY this shape:
{{
  "ats_score": <number 0-100>,
  "missing_skills": [<string>, ...],
  "skill_gap_analysis": {{
     "strengths": [<string>, ...],
     "gaps": [<string>, ...]
  }},
  "career_suggestions": [
     {{"role": <string>, "fit_reason": <string>}}
  ],
  "roadmap": {{
     "next_3_months": [<string>, ...],
     "next_6_months": [<string>, ...],
     "next_12_months": [<string>, ...]
  }}
}}
"""
    result = ai_complete_json(prompt, system=system, fallback=fallback)
    # Defensive merge in case the model omits a key
    for key, value in fallback.items():
        result.setdefault(key, value)
    return result
