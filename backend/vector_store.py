"""
vector_store.py
Qdrant integration: insert, search, and delete candidate embeddings.
"""

from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from match import get_embedding
from pdf_parser import extract_text_from_pdf

COLLECTION_NAME = "candidates"
VECTOR_SIZE = 384  # matches all-MiniLM-L6-v2's output dimension

client = QdrantClient(host="localhost", port=6333)

# A create table in the database function
def create_collection() -> None:
    """Create the candidates collection if it doesn't already exist."""
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection '{COLLECTION_NAME}'.")

# Insert data to the table function
def insert_candidate(point_id: int, name: str, cv_text: str) -> None:
    """Embed a candidate's CV text and upsert it into Qdrant."""
    embedding = get_embedding(cv_text)

    point = PointStruct(
        id=point_id,
        vector=embedding.tolist(),
        payload={"name": name, "cv_text": cv_text},
    )

    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    print(f"Inserted candidate '{name}' (id={point_id})")

# search for a data in the table function
def search_candidates(query_text: str, top_k: int = 3) -> list[tuple[str, float]]:
    """Search for the top-K most similar candidates to a query."""
    query_embedding = get_embedding(query_text)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=top_k,
    ).points

    # return [(hit.payload["name"], round(hit.score, 4)) for hit in results]
    return [
        (hit.id,hit.payload["name"], round(hit.score, 4), hit.payload.get("cv_text", ""))
        for hit in results
    ]

# delete a data in the table function
def delete_candidate(point_id: int) -> None:
    """Delete a candidate point from the collection by ID."""
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[point_id],
    )
    print(f"Deleted candidate (id={point_id})")

# check if a particular data exists before deleting
def candidate_exists(point_id: int) -> bool:
    """Check whether a point with the given ID currently exists."""
    result = client.retrieve(collection_name=COLLECTION_NAME, ids=[point_id])
    return len(result) > 0

def reset_collection() -> None:
    """Delete and recreate the Qdrant collection — used when resetting candidates
    so Qdrant point IDs realign with Postgres candidate IDs restarting at 1."""
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    create_collection()


if __name__ == "__main__":
    create_collection()

    cv_dir = Path("data/sample_cvs")
    cv_paths = list(cv_dir.glob("*.pdf"))

    if not cv_paths:
        print(f"No CVs found in {cv_dir}.")
    else:
        print(f"Inserting {len(cv_paths)} candidates...\n")
        for i, cv_path in enumerate(cv_paths, start=1):
            cv_text = extract_text_from_pdf(str(cv_path))
            insert_candidate(point_id=i, name=cv_path.stem, cv_text=cv_text)

        query = "Python Backend Engineer"
        print(f"\nSearching for: \"{query}\"\n")
        for name, score,cv_text in search_candidates(query, top_k=3):
            print(f"{name} — {score}")

        # Demonstrate delete on the last-inserted candidate
        last_id = len(cv_paths)
        print(f"\nDeleting candidate id={last_id} to test delete_candidate()...")
        print(f"Exists before delete: {candidate_exists(last_id)}")
        #delete_candidate(last_id)
        print(f"Exists after delete: {candidate_exists(last_id)}")

        print(f"\nSearching again after delete: \"{query}\"\n")
        for name, score,cv_text in search_candidates(query, top_k=3):
            print(f"{name} — {score}")