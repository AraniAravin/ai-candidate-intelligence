"""
pdf_parser.py
Extracts raw text from a PDF CV using PyMuPDF.
"""

import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract raw text from a PDF file.

    Args:
        pdf_path: path to the PDF file

    Returns:
        the extracted text as a single string
    """
    text_parts = []

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            text_parts.append(page_text)

    full_text = "\n".join(text_parts)
    return full_text


def save_text(text: str, output_path: str) -> None:
    """Save extracted text to a .txt file."""
    Path(output_path).write_text(text, encoding="utf-8")


def process_cv(pdf_path: str, output_dir: str) -> str:
    """
    Full pipeline: PDF -> raw text -> saved .txt file.

    Args:
        pdf_path: path to input PDF
        output_dir: directory to save the .txt output

    Returns:
        path to the saved .txt file
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    text = extract_text_from_pdf(str(pdf_path))

    output_path = output_dir / f"{pdf_path.stem}.txt"
    save_text(text, str(output_path))

    return str(output_path)


if __name__ == "__main__":
    input_dir = Path("data/sample_cvs")
    output_dir = Path("data/extracted_text")

    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_dir}. Add some CVs first.")
    else:
        print(f"Found {len(pdf_files)} PDF(s). Processing...\n")
        for pdf_file in pdf_files:
            output_path = process_cv(str(pdf_file), str(output_dir))
            print(f"{pdf_file.name} → {output_path}")

