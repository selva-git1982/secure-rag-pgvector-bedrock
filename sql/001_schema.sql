CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    department TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    CHECK (jsonb_typeof(metadata->'allowed_roles') = 'array')
);

CREATE INDEX IF NOT EXISTS idx_chunks_tenant_department
    ON document_chunks (tenant_id, department);
CREATE INDEX IF NOT EXISTS idx_chunks_allowed_roles
    ON document_chunks USING GIN ((metadata->'allowed_roles'));

CREATE TABLE IF NOT EXISTS rag_retrieval_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    query_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retrieved_document_ids TEXT[] NOT NULL
);

-- For a populated dataset, benchmark and choose ONE ANN index in sql/002_indexes.sql.
