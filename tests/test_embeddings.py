import math
import pytest
from app.embeddings import DIMENSIONS, local_embedding


def test_local_embedding_deterministic_and_normalized():
    a = local_embedding("Synthetic quality deviation record")
    b = local_embedding("Synthetic quality deviation record")
    assert a == b
    assert len(a) == DIMENSIONS
    assert math.isclose(sum(x*x for x in a), 1.0, abs_tol=1e-10)


def test_empty_text_rejected():
    with pytest.raises(ValueError):
        local_embedding("   ")
