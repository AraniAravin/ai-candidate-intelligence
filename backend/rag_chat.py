"""
rag_chat.py
Basic RAG pipeline: question -> embed -> retrieve from Qdrant ->
inject as context -> generate answer with local LLM.
"""

import ollama

from vector_store import search_candidates

MODEL_NAME = "llama3.2"

RAG_PROMPT_TEMPLATE = """You are an assistant helping a recruiter understand candidate matches.

Use ONLY the candidate information below to answer the question. If the information isn't enough to answer confidently, say so honestly instead of guessing.

RETRIEVED CANDIDATE INFORMATION:
{context}

QUESTION:
{question}

ANSWER:"""


def retrieve_context(question: str, top_k: int = 3) -> str:
    """
    Retrieval step: search Qdrant for candidates relevant to the question,
    and format their info as context text for the LLM.
    """
    results = search_candidates(question, top_k=top_k)

    context_parts = []
    for name, score,cv_text in results:
        context_parts.append(f"- {name} (similarity score: {score})")
        # context_parts.append(
        #     f"- {name} (similarity score: {score})\n  CV: {cv_text}"
        # )


    return "\n".join(context_parts)


def generate_answer(question: str, context: str) -> str:
    """
    Generation step: send the question + retrieved context to the LLM.
    """
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"].strip()


def rag_answer(question: str, top_k: int = 3) -> str:
    """
    Full RAG pipeline: retrieval + augmentation + generation.
    """
    context = retrieve_context(question, top_k=top_k)

    if not context:
        return "I couldn't find any relevant candidate information to answer that."

    answer = generate_answer(question, context)
    return answer


if __name__ == "__main__":
    question = "Why is the top-ranked candidate a good fit for a Python AI Engineer role?"

    print(f"Question: {question}\n")

    context = retrieve_context(question)
    print("Retrieved context:")
    #print(context)
    print()

    answer = generate_answer(question, context)
    print("Answer:")
    print(answer)