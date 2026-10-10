# FAISS vector-retrieval scalability protocol

This experiment isolates vector search from embedding generation and multimodal ranking. NumPy brute-force cosine retrieval is compared with exact `faiss.IndexFlatIP` and approximate `faiss.IndexHNSWFlat` over the same L2-normalized float32 vectors.

- Seed: `20261010`
- Dimension: 768
- Collection sizes: 100, 1,000, 10,000, 50,000 and 100,000
- Queries: 50 fixed normalized vectors
- Retrieved neighbors: 10
- Ground truth: stable full sort of NumPy inner-product scores
- HNSW: M=32, efConstruction=80, efSearch=64

Recall@K is overlap with the brute-force top K divided by K. Model inference, model loading, embedding generation and multimodal weights are outside the timed search section. Synthetic vector generation is measured separately. Index build time is excluded from query latency.

The memory column estimates retained vector/index storage. Flat storage is `count × dimension × 4` bytes. HNSW additionally estimates `2 × M` 32-bit neighbor links per vector; allocator and library overhead are not included.

The integration check used cached MiniLM text embeddings from the 24 `campus_v1` development queries and 48 found candidates before the later E5 production selection. It validates only vector-neighbor equivalence and does not modify `rank_reports()`.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-evaluation.txt
.\.venv\Scripts\python.exe -m scripts.benchmark_faiss
```
