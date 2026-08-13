"""
extract_job_info.py
Sends a job description to a local LLM (via Ollama) and extracts
a structured job profile as JSON.
"""

import json
import re
from pathlib import Path

import ollama

MODEL_NAME = "llama3.2"

# EXTRACTION_PROMPT_TEMPLATE = """You are an information extraction system. Extract job requirement information from the job description below.

# Return ONLY valid JSON, with no explanation, no markdown code fences, and no extra text before or after. Use this exact structure:

# {{
#   "role": "string or null if not found",
#   "required_skills": ["list", "of", "required", "skills"],
#   "experience_required": number or null if not determinable
# }}

# Rules:
# - If a field cannot be found in the text, use null (for strings/numbers) or an empty list (for required_skills).
# - Do not invent or guess skills that are not mentioned or clearly implied in the text.
# - experience_required should be the minimum years of experience requested, as a number. If a range is given (e.g. "3-5 years"), use the lower bound.

# JOB DESCRIPTION:
# \"\"\"
# {job_text}
# \"\"\"

# JSON:"""
EXTRACTION_PROMPT_TEMPLATE = """You are an information extraction system. Extract job requirement information from the job description below.

Return ONLY valid JSON, with no explanation, no markdown code fences, and no extra text before or after. Use this exact structure:

{{
  "role": "string or null if not found",
  "required_skills": ["list", "of", "must-have", "skills"],
  "nice_to_have_skills": ["list", "of", "bonus", "or", "preferred", "skills"],
  "experience_required": number or null if not determinable
}}

Rules:
- Treat all skills listed under a "Requirements" section/header as required_skills by default, 
  UNLESS they are explicitly marked as "bonus", "preferred", "a plus", "nice to have", or similar.
- Do not infer a skill is optional just because of softer phrasing like "familiarity with" — 
  only classify it as nice_to_have_skills if there is an explicit optional/bonus marker.
- required_skills should ONLY include skills explicitly stated as required, mandatory, or essential.
- nice_to_have_skills should include anything described as "bonus", "preferred", "a plus", "nice to have", or similar — do NOT put these in required_skills.
- If a field cannot be found in the text, use null (for strings/numbers) or an empty list (for skill lists).
- Do not invent or guess skills that are not mentioned or clearly implied in the text.
- experience_required should be the minimum years of experience requested, as a number. If a range is given (e.g. "3-5 years"), use the lower bound.

JOB DESCRIPTION:
\"\"\"
{job_text}
\"\"\"

JSON:"""


def clean_json_response(raw_response: str) -> str:
    """Strip markdown code fences and isolate the JSON object."""
    text = raw_response.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return text.strip()


def extract_job_info(job_text: str) -> dict:
    """Send job description text to the local LLM and return structured job info."""
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(job_text=job_text)
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    raw_output = response["response"]
    cleaned = clean_json_response(raw_output)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"  ⚠ Failed to parse JSON. Raw output was:\n{raw_output}\n")
        raise e


if __name__ == "__main__":
    job_description = """Mandatory Technical Skills

* .NET / C#
* Python
* SQL
* React / Next.js
* REST APIs & API Integration
* AI / LLM / AI API Integration


Requirements

* Minimum 2+ years of Full Stack Software Development experience.
* Strong Functional and Technical knowledge.
* Ability to understand business processes and independently develop practical software solutions.
* Strong interest in AI, automation, and emerging technologies.
* Ability to work with changing requirements and develop flexible solutions.
* Strong analytical and problem-solving skills.
* Ability to work independently while collaborating with the Headquarters IT & Intelligence Team.
* Willingness to learn, experiment, and introduce new technology ideas to the organization.
"""

    print("Processing job description...\n")
    profile = extract_job_info(job_description)
    print(json.dumps(profile, indent=2))