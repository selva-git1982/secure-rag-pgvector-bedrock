"""Parameter-bound, authorization-aware SQL retrieval and transactional audit."""
import json
import os

import psycopg
from pgvector.psycopg import register_vector

from app.security import Principal

# Authorization predicates are inside SQL, not applied after results reach the model.
# ?| checks whether any of the principal's roles appears in allowed_roles.
RETRIEVE_SQL = """
SELECT chunk_id, document_id, content, embedding <=> %(vector)s AS distance
FROM document_chunks
WHERE tenant_id = %(tenant_id)s
  AND department = %(department)s
  AND (metadata->'allowed_roles') ?| %(roles)s::text[]
ORDER BY embedding <=> %(vector)s
LIMIT %(limit)s
"""


def connection():
    conn = psycopg.connect(os.environ["DATABASE_URL"])
    register_vector(conn)
    return conn


def retrieve(principal: Principal, vector: list[float], limit: int = 5) -> list[dict]:
    params = {
        "tenant_id": principal.tenant_id,
        "department": principal.department,
        "roles": list(principal.roles),
        "vector": vector,
        "limit": limit,
    }
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(RETRIEVE_SQL, params)
            rows = cur.fetchall()
            results = [
                {"chunk_id": row[0], "document_id": row[1], "content": row[2], "distance": float(row[3])}
                for row in rows
            ]
            cur.execute(
                """INSERT INTO rag_retrieval_audit (user_id, retrieved_document_ids)
                   VALUES (%s, %s::text[])""",
                (principal.user_id, list(dict.fromkeys(r["document_id"] for r in results))),
            )
        # Transaction commits only if retrieval and audit insertion both succeed.
    return results


def insert_chunk(document_id: str, tenant_id: str, department: str,
                 content: str, allowed_roles: list[str], vector: list[float]) -> None:
    metadata = {"allowed_roles": allowed_roles, "classification": "synthetic",
                "document_version": "1.0"}
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO document_chunks
                   (document_id, tenant_id, department, content, metadata, embedding)
                   VALUES (%s, %s, %s, %s, %s::jsonb, %s)""",
                (document_id, tenant_id, department, content, json.dumps(metadata), vector),
            )
