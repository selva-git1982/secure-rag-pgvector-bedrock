"""Retrieval-only API. Generation is deliberately not enabled by default."""
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.embeddings import embed
from app.repository import retrieve
from app.security import Principal, authenticate

app = FastAPI(title="Secure RAG Retrieval Reference", version="0.1.0")


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


class ChunkResult(BaseModel):
    chunk_id: int
    document_id: str
    content: str
    distance: float


class QueryResponse(BaseModel):
    results: list[ChunkResult]
    notice: str = "Reference retrieval only; no LLM generation or compliance certification"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/retrieve", response_model=QueryResponse)
def query(request: QueryRequest, principal: Annotated[Principal, Depends(authenticate)]):
    try:
        vector = embed(request.query)
        return QueryResponse(results=retrieve(principal, vector, request.limit))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
