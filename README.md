# Secure RAG with PostgreSQL/pgvector and Amazon Bedrock

**Reference implementation accompanying:** *Beyond Vector Search: Engineering Secure and High-Performance RAG Pipelines* (DZone article; publication link to be added **after publication**).

This is an **illustrative, synthetic-data, retrieval-only** reference implementation. It is **not** a validated healthcare application, a production-ready authorization service, a HIPAA/GxP/21 CFR Part 11 compliance solution, or evidence of deployment at any organization.

## What it demonstrates

- 1,024-dimensional embeddings in PostgreSQL/pgvector
- Relational `tenant_id` and `department` columns, with JSONB `allowed_roles`
- Signed JWT identity claims; the request body cannot select its own tenant or roles
- SQL-level authorization **before** retrieved content is returned
- Multi-role authorization with PostgreSQL JSONB `?|` operator
- Transactional audit insertion with returned document identifiers
- Optional Amazon Bedrock Titan Text Embeddings V2, plus a **non-semantic** deterministic local hashing mode for quick demos
- HNSW/IVFFlat index examples, with no unsupported performance benchmarks

## Architecture

```text
Signed bearer token --> API authentication --> Trusted Principal
                                           |
Query --> Embedding provider --------------+--> PostgreSQL/pgvector
                                                 | tenant + department + roles
                                                 | cosine-distance ranking
                                                 +--> retrieved chunks
                                                 +--> retrieval audit log
```

**No language-model generation is performed by this implementation.** Amazon Bedrock is used only for embeddings when configured. Generation, source citation validation, document-level ACL sync, key rotation, policy engines, tenant-specific DB isolation, and full regulatory audit controls are outside this example's scope.

## Quick start (local, synthetic data)

Requires Python 3.11+, Docker Compose, and a shell.

```bash
cp .env.example .env
# Edit .env and set JWT_SECRET to a unique random secret of at least 32 characters.
docker compose up -d db
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
set -a; source .env; set +a
python -m scripts.seed
uvicorn app.main:app --reload
```

In another shell, with the same environment variables loaded:

```bash
TOKEN=$(python -m scripts.make_demo_token)
curl -s http://127.0.0.1:8000/retrieve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"synthetic deviation review", "limit":5}'
```

The synthetic `qa_reviewer` token can retrieve `SYN-QA-001`, but must not retrieve a manager-only document, a Research department document, or another tenant's document. The local hashing embeddings are **not semantically meaningful** and must never be used to make quality/recall claims.

Check the audit trail:

```bash
docker compose exec db psql -U rag -d rag -c \
  'SELECT audit_id, user_id, query_timestamp, retrieved_document_ids FROM rag_retrieval_audit;'
```

## Amazon Bedrock embeddings (optional)

Set `EMBEDDING_PROVIDER=bedrock` and configure AWS credentials/permissions for `bedrock:InvokeModel` on the selected Titan embedding model. Ensure model access and region availability. **Recreate and reseed the demo database after switching embedding providers**: query and stored embeddings must use the same model and dimension. Model invocations may incur AWS charges.

## Vector indexes and query planning

- Schema and B-tree/GIN indexes: `sql/001_schema.sql`
- **Alternative** HNSW/IVFFlat examples: `sql/002_indexes.sql`
- Benchmark filtered queries with `EXPLAIN (ANALYZE, BUFFERS)` using bound values in your SQL client. Compare latency and authorized recall across tenant/department/role selectivity.
- `CREATE INDEX` statements are intentionally **not automatically applied** for ANN indexes; choose an approach after loading representative data.

## Security limitations

This demo verifies HS256 JWT signatures, expiration, issuer, and audience, but **does not provide an identity provider**, revocation, JWKS rotation, or enterprise authorization policy integration. In production, use a trusted IdP and policy engine, short-lived credentials, least-privilege database roles, encrypted transport, secure secrets management, row-level security where appropriate, robust observability, and independently reviewed access-control rules. The illustrative department equality filter may be too restrictive for cross-department authorized users. Database owners/admins and ingestion scripts have broader privileges than query users; production separation is required.

The retrieval audit table is a **basic operational log**, not an immutable/tamper-evident regulated audit trail. It does not prove generated-response provenance or compliance. Avoid sensitive content and identifiers in logs; set retention and access controls.

## Testing

```bash
python -m pytest -q
```

Unit tests cover JWT claim validation, deterministic demo embeddings, and the presence of SQL authorization predicates. **They do not constitute a database integration test, penetration test, recall benchmark, or regulatory validation.**

## Reference and citation

Article: *Beyond Vector Search: Engineering Secure and High-Performance RAG Pipelines*, Selvamurugan Ramamoorthy, DZone (**URL pending publication**).

If you reuse the code, cite this repository URL after uploading it to GitHub. Do not present this repository as a production deployment or third-party independent verification.

## License

MIT. See [LICENSE](LICENSE).
