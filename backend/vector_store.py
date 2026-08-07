"""
vector_store.py
Stores candidate embeddings in Qdrant and performs similarity search
for top-K candidate retrieval.
"""

from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from pdf_parser import extract_text_from_pdf
from match import get_embedding

COLLECTION_NAME = "candidates"
VECTOR_SIZE = 384  # matches all-MiniLM-L6-v2's output dimension

client = QdrantClient(host="localhost", port=6333)

# this method checks if a collection exists or not and if not creates a collection 
def create_collection() -> None:
    """Create the candidates collection if it doesn't already exist."""
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        #vector format configuration
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection '{COLLECTION_NAME}'.")


def store_candidate(point_id: int, name: str, cv_text: str) -> None:
    """Embed a candidate's CV text and upsert it into Qdrant."""
    embedding = get_embedding(cv_text)

    point = PointStruct(
        id=point_id,
        vector=embedding.tolist(),
        payload={"name": name, "cv_text": cv_text},
    )

    client.upsert(collection_name=COLLECTION_NAME, points=[point])


def search_candidates(query_text: str, top_k: int = 3):
    """Search for the top-K most similar candidates to a query."""
    query_embedding = get_embedding(query_text)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=top_k,
    ).points

    return [(hit.payload["name"], round(hit.score, 4)) for hit in results]


if __name__ == "__main__":
    create_collection()

    cv_dir = Path("data/sample_cvs")
    cv_paths = list(cv_dir.glob("*.pdf"))

    if not cv_paths:
        print(f"No CVs found in {cv_dir}.")
    else:
        print(f"Storing {len(cv_paths)} candidates in Qdrant...\n")
        for i, cv_path in enumerate(cv_paths, start=1):
            cv_text = extract_text_from_pdf(str(cv_path))
            candidate_name = cv_path.stem
            store_candidate(point_id=i, name=candidate_name, cv_text=cv_text)
            print(f"Stored: {candidate_name}")

        query = "We are hiring a Python backend developer with experience building REST APIs using FastAPI. Experience with PostgreSQL and Docker is required."
        print(f"\nSearching for: \"{query}\"\n")
        results = search_candidates(query, top_k=3)

        print("Top matches:")
        for name, score in results:
            print(f"{name} — {score}")