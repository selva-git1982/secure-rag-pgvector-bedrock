import pytest
from app.security import parse_claims


def test_principal_parses_multiple_roles():
    p = parse_claims({"sub": "user1", "tenant_id": "t1", "department": "QA",
                      "roles": ["reviewer", "manager", "reviewer"]})
    assert p.roles == ("manager", "reviewer")
    assert p.tenant_id == "t1"


def test_missing_claims_rejected():
    with pytest.raises(ValueError):
        parse_claims({"sub": "user1", "tenant_id": "t1", "department": "QA", "roles": []})
