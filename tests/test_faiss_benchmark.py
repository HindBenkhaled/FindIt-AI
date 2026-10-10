import numpy as np
import pytest

faiss = pytest.importorskip("faiss")

from scripts.benchmark_faiss import brute_search, normalize, overlap_recall


def test_index_flat_ip_matches_brute_force():
    rng = np.random.default_rng(7)
    vectors = normalize(rng.standard_normal((250, 32), dtype=np.float32))
    queries = normalize(rng.standard_normal((5, 32), dtype=np.float32))
    index = faiss.IndexFlatIP(32)
    index.add(vectors)
    for query in queries:
        expected = brute_search(vectors, query, 10)
        _, actual = index.search(query[None, :], 10)
        assert overlap_recall(actual[0], expected, 10) == 1.0
        assert np.array_equal(actual[0], expected)


def test_normalize_produces_unit_vectors():
    vectors = normalize(np.array([[3., 4.], [1., 1.]], dtype=np.float32))
    assert np.linalg.norm(vectors, axis=1) == pytest.approx([1., 1.])
