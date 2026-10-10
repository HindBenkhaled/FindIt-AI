import numpy as np


def test_text_cache_key_changes_with_model(monkeypatch, tmp_path):
    from src import embeddings

    calls = []

    class FakeModel:
        def encode(self, text, **kwargs):
            calls.append((embeddings.TEXT_MODEL, text))
            return np.array([1., 0.], dtype=np.float32)

    monkeypatch.setattr(embeddings, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(embeddings, "load_model", lambda model: FakeModel())
    monkeypatch.setattr(embeddings, "TEXT_MODEL", "model-a")
    embeddings.text_embedding("same report")
    embeddings.text_embedding("same report")
    monkeypatch.setattr(embeddings, "TEXT_MODEL", "model-b")
    embeddings.text_embedding("same report")

    assert calls == [("model-a", "same report"), ("model-b", "same report")]
    assert len(list(tmp_path.glob("*.npy"))) == 2
