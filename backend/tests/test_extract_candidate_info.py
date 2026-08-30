import json

from extract_candidate_info import clean_json_response, extract_candidate_info


def test_clean_json_response_strips_markdown_fences():
    raw = '```json\n{"name": "Jane"}\n```'
    cleaned = clean_json_response(raw)
    assert cleaned == '{"name": "Jane"}'


def test_clean_json_response_handles_plain_json():
    raw = '{"name": "Jane"}'
    cleaned = clean_json_response(raw)
    assert cleaned == '{"name": "Jane"}'


def test_extract_candidate_info_parses_mocked_llm_response(monkeypatch):
    fake_response = {
        "response": json.dumps({
            "name": "Jane Doe",
            "skills": ["Python", "FastAPI"],
            "experience_years": 3,
            "education": "Computer Science",
        })
    }

    def fake_generate(model, prompt, **kwargs):
        return fake_response

    import extract_candidate_info as module
    monkeypatch.setattr(module.ollama, "generate", fake_generate)

    result = extract_candidate_info("some CV text")

    assert result["name"] == "Jane Doe"
    assert "Python" in result["skills"]
    assert result["experience_years"] == 3