"""
extract_candidate_info.py
Sends raw CV text to a local LLM (via Ollama) and extracts
structured candidate information as JSON.
"""

import json
import re
from pathlib import Path

import ollama

MODEL_NAME = "llama3.2"

EXTRACTION_PROMPT_TEMPLATE = """You are an information extraction system. Extract candidate information from the CV text below.

Return ONLY valid JSON, with no explanation, no markdown code fences, and no extra text before or after. Use this exact structure:

{{
  "name": "string or null if not found",
  "skills": ["list", "of", "skills"],
  "experience_years": number or null if not determinable,
  "education": "string or null if not found"
}}

Rules:
- If a field cannot be found in the text, use null (for strings/numbers) or an empty list (for skills).
- Do not invent or guess information that is not present in the text.
- experience_years should be your best estimate of total years of professional experience, as a number.

CV TEXT:
\"\"\"
{cv_text}
\"\"\"

JSON:"""


def clean_json_response(raw_response: str) -> str:
    """
    Strip markdown code fences and any leading/trailing text
    the model might add despite instructions.
    """
    text = raw_response.strip()

    # Remove ```json ... ``` or ``` ... ``` fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # If there's extra text, try to isolate the {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return text.strip()


def extract_candidate_info(cv_text: str) -> dict:
    """
    Send CV text to the local LLM and return structured candidate info.
    """
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(cv_text=cv_text)

    response = ollama.generate(model=MODEL_NAME, prompt=prompt,options={"num_predict": 1024})
    raw_output = response["response"]
    finish_reason = response.get("done_reason")

    cleaned = clean_json_response(raw_output)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        if finish_reason == "length":
            print(f"  ⚠ Response was truncated (hit num_predict limit). Consider raising num_predict.")
        print(f"  ⚠ Failed to parse JSON. Raw output was:\n{raw_output}\n")
        raise e


if __name__ == "__main__":
    text_dir = Path("data/extracted_text")
    txt_files = list(text_dir.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {text_dir}. Run pdf_parser.py first.")
    else:
        for txt_file in txt_files:
            cv_text = txt_file.read_text(encoding="utf-8")
            print(f"Processing {txt_file.name}...")

            try:
                profile = extract_candidate_info(cv_text)
                print(json.dumps(profile, indent=2))
            except Exception as e:
                print(f"  Error: {e}")

            print("-" * 50)