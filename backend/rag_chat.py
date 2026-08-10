# """
# rag_chat.py // Day 10 Generic Version for understanding
# Basic RAG pipeline: question -> embed -> retrieve from Qdrant ->
# inject as context -> generate answer with local LLM.
# """

# import ollama

# from vector_store import search_candidates

# MODEL_NAME = "llama3.2"

# RAG_PROMPT_TEMPLATE = """You are an assistant helping a recruiter understand candidate matches.

# Use ONLY the candidate information below to answer the question. If the information isn't enough to answer confidently, say so honestly instead of guessing.

# RETRIEVED CANDIDATE INFORMATION:
# {context}

# QUESTION:
# {question}

# ANSWER:"""


# def retrieve_context(question: str, top_k: int = 3) -> str:
#     """
#     Retrieval step: search Qdrant for candidates relevant to the question,
#     and format their info as context text for the LLM.
#     """
#     results = search_candidates(question, top_k=top_k)

#     context_parts = []
#     for name, score,cv_text in results:
#         context_parts.append(f"- {name} (similarity score: {score})")
#         # context_parts.append(
#         #     f"- {name} (similarity score: {score})\n  CV: {cv_text}"
#         # )


#     return "\n".join(context_parts)


# def generate_answer(question: str, context: str) -> str:
#     """
#     Generation step: send the question + retrieved context to the LLM.
#     """
#     prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)
#     response = ollama.generate(model=MODEL_NAME, prompt=prompt)
#     return response["response"].strip()


# def rag_answer(question: str, top_k: int = 3) -> str:
#     """
#     Full RAG pipeline: retrieval + augmentation + generation.
#     """
#     context = retrieve_context(question, top_k=top_k)

#     if not context:
#         return "I couldn't find any relevant candidate information to answer that."

#     answer = generate_answer(question, context)
#     return answer


# if __name__ == "__main__":
#     question = "Why is the top-ranked candidate a good fit for a Python AI Engineer role?"

#     print(f"Question: {question}\n")

#     context = retrieve_context(question)
#     print("Retrieved context:")
#     #print(context)
#     print()

#     answer = generate_answer(question, context)
#     print("Answer:")
#     print(answer)

"""
rag_chat.py
RAG pipeline for candidate Q&A.

Two modes:
1. generic RAG (Day 10) - open-ended questions, retrieval via similarity search
2. targeted RAG (Day 11) - "why is Candidate X a good fit for this job?",
   retrieval via direct lookup of a known candidate + job
"""

import ollama

from vector_store import search_candidates, client, COLLECTION_NAME
from match import get_embedding
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "llama3.2"

# ---------- Day 10: generic RAG (kept as-is) ----------

RAG_PROMPT_TEMPLATE = """You are an assistant helping a recruiter understand candidate matches.

Use ONLY the candidate information below to answer the question. If the information isn't enough to answer confidently, say so honestly instead of guessing.

RETRIEVED CANDIDATE INFORMATION:
{context}

QUESTION:
{question}

ANSWER:"""


def retrieve_context(question: str, top_k: int = 3) -> str:
    results = search_candidates(question, top_k=top_k)
    return "\n".join(f"- {name} (similarity score: {score})" for name, score in results)


def generate_answer(question: str, context: str) -> str:
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"].strip()


def rag_answer(question: str, top_k: int = 3) -> str:
    context = retrieve_context(question, top_k=top_k)
    if not context:
        return "I couldn't find any relevant candidate information to answer that."
    return generate_answer(question, context)


# ---------- Day 11: targeted RAG for "why is Candidate X ranked #1?" ----------

EXPLANATION_PROMPT_TEMPLATE = """You are an assistant helping a recruiter understand why a specific candidate matches a job.

JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

CANDIDATE: {candidate_name}
CANDIDATE CV:
\"\"\"
{cv_text}
\"\"\"

SEMANTIC MATCH SCORE: {score}% (higher means more similar to the job description)

Based ONLY on the information above, explain in 2-4 sentences why this candidate does or doesn't appear to be a good fit for the job. Reference specific skills or experience from the CV. Do not invent information not present above.

EXPLANATION:"""


def get_candidate_by_name(candidate_name: str) -> dict | None:
    """
    Direct lookup: scroll through the collection to find a candidate
    by name in the payload (small-scale approach for now).
    """
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
    )
    for point in results:
        if point.payload.get("name") == candidate_name:
            return {"id": point.id, "cv_text": point.payload.get("cv_text", "")}
    return None


def explain_ranking(candidate_name: str, job_description: str) -> str:
    """
    Targeted RAG: given a known candidate and job, retrieve the candidate's
    actual data directly, compute the match score, and generate a grounded
    explanation.
    """
    candidate = get_candidate_by_name(candidate_name)
    if candidate is None:
        return f"No candidate named '{candidate_name}' found."

    cv_text = candidate["cv_text"]

    # Recompute the semantic score directly, so the explanation is grounded
    # in the same number the ranking pipeline would show
    job_embedding = get_embedding(job_description)
    cv_embedding = get_embedding(cv_text)
    score = round(float(cosine_similarity([job_embedding], [cv_embedding])[0][0]) * 100, 1)

    prompt = EXPLANATION_PROMPT_TEMPLATE.format(
        job_description=job_description,
        candidate_name=candidate_name,
        cv_text=cv_text,
        score=score,
    )

    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"].strip()


if __name__ == "__main__":
    job_description = """
    We are hiring a Python backend developer with experience building
    REST APIs using FastAPI. Experience with PostgreSQL and Docker
    is required.
    """

    candidate_name = "cv"  # replace with a real candidate name from your data

    print(f"Question: Why is {candidate_name} a good fit for this job?\n")
    explanation = explain_ranking(candidate_name, job_description)
    print("Answer:")
    print(explanation)