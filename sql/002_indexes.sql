-- ALTERNATIVES: benchmark one approach, not both automatically.
-- HNSW: can be built before data is loaded.
CREATE INDEX idx_embedding_hnsw
ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- IVFFlat: create AFTER representative vectors are loaded.
-- If switching to IVFFlat, drop the HNSW index first.
-- DROP INDEX IF EXISTS idx_embedding_hnsw;
-- CREATE INDEX idx_embedding_ivfflat
-- ON document_chunks USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);
