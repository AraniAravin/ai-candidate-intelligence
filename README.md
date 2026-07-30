# ai-candidate-intelligence

\## Progress Log



\### Day 1 — Foundations + First Embedding Experiment

\- Set up project structure, virtual environment, and dependencies.

\- Learned what embeddings and cosine similarity are, and why they outperform keyword matching for semantic tasks.

\- Ran a first experiment comparing a job description against 5 CV snippets using `all-MiniLM-L6-v2`.

\- Confirmed that semantically related text (e.g., "Python backend developer" vs "Developed APIs using Python and FastAPI") scores highly similar even without exact keyword overlap.

### Day 2 — Sentence Transformers & match.py
- Learned how Sentence Transformers differ from word-level embeddings, and what vector dimensionality means/why it matters.
- Built `backend/match.py`: a reusable script that embeds a job description and multiple candidate texts, then ranks candidates by cosine similarity.
- Tested with [N] candidates, verified ranking matches human intuition.
- when trying unrelated words they still scored above 0.15 not 0 and when the exact words are tried a score of 1 is given
