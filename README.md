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

### Day 6 — Full Semantic Matching Pipeline
- Combined Days 1–5 into `backend/pipeline.py`: an end-to-end pipeline
  that takes a job description and multiple CV PDFs, and returns
  candidates ranked by semantic similarity.
- Tested against 4 CVs and different job descriptions for various roles.
- Confirmed rankings shift sensibly when the job description changes.

## 🎯 Week 1 Milestone — Complete
Built the core AI component: Job Description + CV → Embedding →
Semantic Similarity → Ranked Match Score. Fully working locally,
no external API dependency (uses local sentence-transformers model).

### Day 8 — Vector Database (Qdrant)
- Learned why vector databases exist separately from relational DBs —
  similarity search via indexing (e.g., HNSW) vs exact-match queries.
- Ran Qdrant locally via Docker with a persistent volume.
- Built `backend/vector_store.py`: stores candidate embeddings in Qdrant
  and performs top-K similarity search.
- Verified Qdrant's search results match my Day 6 brute-force cosine
  similarity implementation — confirms correctness, not just speed.

  ### Day 9 — Qdrant CRUD Interface
- Extended `vector_store.py` from Day 8 into a full insert/search/delete
  interface, matching the shape backend routes will call directly.
- Verified full lifecycle: insert → search → delete → confirm removal → search again.
- When deleteting a non existent ID from QDrant, it does nor throw an error instead it just throws a acknwoledged status (here it will be False) as Qdrant delete() operation is idempotent so the whole purpose of it to to make sure the id not does exist now than if it ever existed before, so to avoid any edge case issue we have a function called candidate_exists() to check if the candidate ever existed.
- ID Strategy for the week will be once a structured DB like postgresql is created and candidate details will be stored in it firstly, generating a unique primary key for each record, which will be a single source of truth for IDs, which will be stored as the point number for the vector in QDrant in that way the data in both the DB can be kept on sync and no more manual working on it

### Day 10 — RAG Fundamentals
- Learned the Retrieval-Augmented Generation pattern: retrieve relevant
  data (Qdrant), inject as context (augmentation), generate a grounded
  answer (LLM) — and that RAG is an architecture pattern, not a new tool.
- Built `backend/rag_chat.py`, reusing `search_candidates()` from Day 9
  and Ollama from Day 4.
- When the context got enriched like adding the cv_text to it the results produced changed and more validation in the output given was seen comparative to before where no justification was given.
- When a question with no match was given it handled it well by making sure the answer is not fake and to one side and makes sure not enough details is given for the role and it isnt sure of the answer.

### Day 11 — Working RAG Pipeline
- Extended Day 10's generic RAG into targeted RAG: given a known
  candidate and job, directly retrieves that candidate's full CV data
  (not a similarity search) and generates a grounded explanation.
- Explanation is tied to the same semantic score used in ranking,
  so the "why" is consistent with the actual match score shown elsewhere.
- Verified explanations reference real CV content and handle poor-fit
  candidates honestly rather than overselling them.
- Known limitation: candidate lookup uses a full collection scroll —
  fine at current scale, will need proper filtering/indexing once
  PostgreSQL candidate IDs are wired in.