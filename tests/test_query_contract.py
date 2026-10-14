from pathlib import Path


def test_authorization_inside_sql():
    source = (Path(__file__).resolve().parents[1] / 'app' / 'repository.py').read_text()
    assert "tenant_id = %(tenant_id)s" in source
    assert "department = %(department)s" in source
    assert "?| %(roles)s::text[]" in source
    assert "LIMIT %(limit)s" in source
