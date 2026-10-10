# FAISS scalability benchmark

Vector search only; model inference, multimodal scoring and model loading are excluded.

| Vectors | Method | Recall@1 | Recall@5 | Recall@10 | Avg ms | Median ms | P95 ms | Build ms | Approx memory MiB |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | NumPy brute force | ground truth | ground truth | ground truth | 0.015 | 0.012 | 0.038 | 0.000 | 0.29 |
| 100 | FAISS IndexFlatIP | 1.000 | 1.000 | 1.000 | 0.014 | 0.013 | 0.019 | 0.116 | 0.29 |
| 100 | FAISS HNSWFlat | 1.000 | 1.000 | 1.000 | 0.033 | 0.032 | 0.036 | 11.583 | 0.32 |
| 1,000 | NumPy brute force | ground truth | ground truth | ground truth | 0.213 | 0.212 | 0.240 | 0.000 | 2.93 |
| 1,000 | FAISS IndexFlatIP | 1.000 | 1.000 | 1.000 | 0.092 | 0.090 | 0.106 | 2.173 | 2.93 |
| 1,000 | FAISS HNSWFlat | 0.960 | 0.972 | 0.972 | 0.140 | 0.139 | 0.156 | 133.524 | 3.17 |
| 10,000 | NumPy brute force | ground truth | ground truth | ground truth | 2.676 | 2.691 | 3.506 | 0.000 | 29.30 |
| 10,000 | FAISS IndexFlatIP | 1.000 | 1.000 | 1.000 | 3.412 | 3.251 | 5.313 | 13.747 | 29.30 |
| 10,000 | FAISS HNSWFlat | 0.640 | 0.604 | 0.584 | 0.903 | 0.859 | 1.273 | 2456.406 | 31.74 |
| 50,000 | NumPy brute force | ground truth | ground truth | ground truth | 15.567 | 15.436 | 16.982 | 0.000 | 146.48 |
| 50,000 | FAISS IndexFlatIP | 1.000 | 1.000 | 1.000 | 25.744 | 25.373 | 31.463 | 63.721 | 146.48 |
| 50,000 | FAISS HNSWFlat | 0.240 | 0.168 | 0.184 | 1.833 | 1.748 | 2.627 | 58381.945 | 158.69 |
| 100,000 | NumPy brute force | ground truth | ground truth | ground truth | 37.783 | 37.691 | 39.980 | 0.000 | 292.97 |
| 100,000 | FAISS IndexFlatIP | 1.000 | 1.000 | 1.000 | 52.981 | 52.700 | 59.838 | 174.070 | 292.97 |
| 100,000 | FAISS HNSWFlat | 0.120 | 0.108 | 0.108 | 2.823 | 2.614 | 4.364 | 166981.307 | 317.38 |

## Actual FindIt embedding validation

Integration fixture: `sentence-transformers/all-MiniLM-L6-v2` embeddings recorded before the later E5 selection; 24 queries, 48 candidates, 384 dimensions.

FAISS versus brute force: Recall@1 1.000, Recall@5 1.000, Recall@10 1.000, exact top-10 order agreement 1.000.

`IndexFlatIP` is exact over normalized float32 vectors. HNSW uses M=32, efConstruction=80, and efSearch=64.
