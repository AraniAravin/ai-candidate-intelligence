from pdf_parser import extract_text_from_pdf


def test_extracts_readable_text(sample_pdf):
    pdf_path = sample_pdf("Python developer with FastAPI experience")
    text = extract_text_from_pdf(pdf_path)

    assert "Python" in text
    assert "FastAPI" in text


def test_empty_page_returns_empty_text(sample_pdf):
    pdf_path = sample_pdf(text="")
    text = extract_text_from_pdf(pdf_path)

    assert text.strip() == ""