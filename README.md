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

  ### Day 12 — FastAPI Application
- Learned core HTTP/API concepts: endpoints, GET vs POST, Pydantic
  validation, request/response models.
- Built `backend/main.py`, wiring together every module from Weeks 1-2
  into a working FastAPI application with 5 endpoints:
  GET /health, POST /jobs, POST /candidates/upload,
  POST /candidates/analyze, POST /chat.
- Verified full flow via FastAPI's auto-generated /docs UI.
- Known limitation: jobs and candidates are stored in-memory (plain
  Python dicts) — data does not persist across server restarts.
  PostgreSQL integration is the next step.

  ## Running the project

1. Start Qdrant: `docker start qdrant-db` (or the `docker run` command from Day 8 if not created yet)
2. Activate the virtual environment: `venv\Scripts\activate`
3. Start the API server: `cd backend && uvicorn main:app --reload`
4. Open http://127.0.0.1:8000/docs to explore and test the API

### Day 13 — Robust AI Pipeline in FastAPI
- The core PDF → Text → LLM → Embedding → Qdrant chain was already
  wired in Day 12's `/candidates/analyze` — today focused on making it
  production-honest: per-candidate error handling so one failure doesn't
  block the batch, explicit status tracking (uploaded/processing/analyzed/failed),
  and a new GET /candidates/status endpoint to inspect progress.
- Tested failure paths deliberately: empty/corrupt PDF, and Qdrant
  being unavailable — confirmed both are caught and recorded rather
  than crashing the request.
- Currently when a CV is flagged as failed it isnt given a retryn when analysing new uploads, but there is two ways we could handle this one is by changing the workflow to ask the candidates to upload another file if the issue is with the pdf as there isnt a use of retrying then or the other way is by actually implementing the retry logic inside the existing code as it could have happened due to an LLM truncation or Qdrant hiccup it is worth retrying.

### Day 14 — Week 2 Milestone: AI Backend MVP
- Added `GET /jobs/{job_id}/ranked-candidates`, the final missing piece
  connecting job descriptions to Qdrant-based candidate ranking.
- Verified the full pipeline end-to-end through the API:
  create job → upload CVs → analyze (PDF → text → LLM → embedding → Qdrant)
  → ranked candidates → RAG chat explanation — all via HTTP, not scripts.
- When ranking candidates for a job id, all the candidates from the database is compared and ranked not the candidates for that specific job only, it needs to be rendered as a system
- When a job id which is non existent and is searched, an empty array is returned currently with no error message which is handled to throw a 404 error and a message indicating the missing job id.

## 🎯 Week 2 Milestone — Complete
The AI Candidate Intelligence Platform backend is now a working MVP:
a real FastAPI application exposing the full pipeline from your original
architecture diagram — CV processing, embeddings, vector search, ranking,
and RAG-based explanation — all through HTTP endpoints with auto-generated
API docs.

### Day 15 — PostgreSQL Schema
- Learned relational database design: one-to-many (jobs → applications),
  many-to-many (candidates ↔ skills via a join table), and how
  SQLAlchemy's ORM maps Python classes to real tables.
- Set up PostgreSQL locally via Docker with a persistent volume.
- Defined 6 tables in `backend/models.py`: candidates, jobs, skills,
  candidate_skills (join table), applications, match_results.
- Verified persistence directly — solves the in-memory data loss
  limitation documented on Day 12.
- Known simplification: skill lists on jobs/match_results are stored
  as comma-separated text rather than fully normalized relationships —
  noted as a possible future refactor.

  ### Day 16 — Persisting Candidate Data to PostgreSQL
- Replaced Day 12's in-memory `candidates_db` dict with real PostgreSQL
  persistence via `backend/crud.py`.
- Candidate name, experience, education, CV text, and status now
  persist across restarts. Skills use a get-or-create pattern to avoid
  duplicate skill rows across candidates.
- Verified candidate.id stays consistent between PostgreSQL and Qdrant
  (same ID used as the Qdrant point ID) — this is the link between the
  two databases.
- Jobs remain in-memory for now — deliberately out of scope for today,
  planned for an upcoming day.

  ### Day 17 — Persisting Job Data to PostgreSQL
- Replaced the last remaining in-memory store (`jobs_db`) with real
  PostgreSQL persistence via `backend/crud.py`.
- Job description → LLM extraction → structured profile → PostgreSQL,
  mirroring Day 16's candidate persistence pattern.
- Required/nice-to-have skills stored as comma-separated text (same
  simplification as noted on Day 15) — round-tripped correctly through
  create_job/job_skills_as_list.
- All application state (candidates AND jobs) now fully persists across
  server restarts — the in-memory limitation flagged on Day 12 is resolved.
- Known limitation: job skills aren't deduplicated/normalized against a
  shared table the way candidate skills are — an inconsistency worth
  fixing in a future refactor.