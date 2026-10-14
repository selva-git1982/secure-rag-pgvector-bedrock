"""Validate signed bearer tokens; never trust tenant/role fields in a query body."""
import os
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class Principal:
    user_id: str
    tenant_id: str
    department: str
    roles: tuple[str, ...]


def parse_claims(claims: dict) -> Principal:
    user_id = claims.get("sub")
    tenant_id = claims.get("tenant_id")
    department = claims.get("department")
    roles = claims.get("roles")
    if (not all(isinstance(x, str) and x for x in (user_id, tenant_id, department))
            or not isinstance(roles, list)
            or not roles
            or not all(isinstance(r, str) and r for r in roles)):
        raise ValueError("Missing or invalid identity claims")
    return Principal(user_id, tenant_id, department, tuple(sorted(set(roles))))


def authenticate(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]) -> Principal:
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail="JWT validation is not configured")
    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            audience=os.getenv("JWT_AUDIENCE", "secure-rag-api"),
            issuer=os.getenv("JWT_ISSUER", "secure-rag-demo"),
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
        )
        return parse_claims(claims)
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc
