# ai-candidate-intelligence

## Progress Log



### Day 1 — Foundations + First Embedding Experiment

- Set up project structure, virtual environment, and dependencies.

- Learned what embeddings and cosine similarity are, and why they outperform keyword matching for semantic tasks.

- Ran a first experiment comparing a job description against 5 CV snippets using `all-MiniLM-L6-v2`.

- Confirmed that semantically related text (e.g., "Python backend developer" vs "Developed APIs using Python and FastAPI") scores highly similar even without exact keyword overlap.

### Day 2 — Sentence Transformers & match.py
- Learned how Sentence Transformers differ from word-level embeddings, and what vector dimensionality means/why it matters.
- Built `backend/match.py`: a reusable script that embeds a job description and multiple candidate texts, then ranks candidates by cosine similarity.
- Tested with [N] candidates, verified ranking matches human intuition.
- when trying unrelated words they still scored above 0.15 not 0 and when the exact words are tried a score of 1 is given

### Day 3 — PDF Processing
- Learned how PDFs store content (drawing instructions, not linear text) and why extraction quality varies by PDF source.
- Built `backend/pdf_parser.py` using PyMuPDF to extract raw text from PDF CVs and save as `.txt` files.
- Processed 5 sample CVs. Cvs with different layout format texts get scrambled along the extracted documents and when trying extraction within documents of various languages, languages other than english looks messed and for a page break there is a gibberish display of text before displaying text from the other page and when image of documents are converted to pdf and extraction method tried on it doesnt extract any texts

### Day 4 — Candidate Information Extraction
- Learned about structured LLM outputs, JSON-constrained prompting, and common failure modes (markdown fences, hallucinated fields).
- Set up Ollama locally with the llama3.2 model.
- Built `backend/extract_candidate_info.py`: sends raw CV text to the local LLM and parses structured JSON (name, skills, experience_years, education).
- Tested on 3 CVs. The output was given exactly as described and all gibberish text of the raw text was omitted and unknown outputs was given as null rather than predicting values

### Day 5 — Job Description Extraction
- Applied the same LLM extraction pattern from Day 4 to job descriptions.
- Built `backend/extract_job_info.py`: extracts role, required_skills, and experience_required as structured JSON.
- Tested on some job descriptions across different roles and some JD copied from LinkedIn.
- An issue was spotted with bonus skills where if any preferaable skills are included they are noted down as required skills, it will be handled by optimising the prompt and providing the LLM instructions on how to handle the case explicitly and also being careful about the tone of the description. 
