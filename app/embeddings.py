"""Local deterministic demo embeddings OR Amazon Bedrock Titan Text Embeddings V2."""
import hashlib
import json
import math
import os
import re

DIMENSIONS = 1024


def local_embedding(text: str) -> list[float]:
    """Toy hashing vector for pipeline tests ONLY; not a semantic embedding model."""
    vector = [0.0] * DIMENSIONS
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % DIMENSIONS
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    magnitude = math.sqrt(sum(x * x for x in vector))
    if magnitude == 0:
        raise ValueError("Text must contain at least one alphanumeric token")
    return [x / magnitude for x in vector]


def embed(text: str) -> list[float]:
    provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    if provider == "local":
        return local_embedding(text)
    if provider != "bedrock":
        raise ValueError("EMBEDDING_PROVIDER must be 'local' or 'bedrock'")
    import boto3
    client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    result = client.invoke_model(
        modelId=os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0"),
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text, "dimensions": DIMENSIONS, "normalize": True}),
    )
    vector = json.loads(result["body"].read())["embedding"]
    if len(vector) != DIMENSIONS:
        raise ValueError("Embedding model dimension mismatch")
    return vector
