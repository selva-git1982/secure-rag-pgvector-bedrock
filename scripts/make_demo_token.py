"""LOCAL TEST ONLY: mint a signed token with fictional identity claims."""
import os
import time

import jwt

if __name__ == "__main__":
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32:
        raise SystemExit("Set JWT_SECRET to a random value of at least 32 characters")
    now = int(time.time())
    claims = {
        "iss": os.getenv("JWT_ISSUER", "secure-rag-demo"),
        "aud": os.getenv("JWT_AUDIENCE", "secure-rag-api"),
        "sub": "synthetic-user-001",
        "tenant_id": "healthcare_org_001",
        "department": "Quality Assurance",
        "roles": ["qa_reviewer"],
        "iat": now,
        "exp": now + 3600,
    }
    print(jwt.encode(claims, secret, algorithm="HS256"))
