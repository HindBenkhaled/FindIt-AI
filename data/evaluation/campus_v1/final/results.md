# Frozen campus_v1 held-out evaluation

The frozen E5 + SigLIP system was evaluated once on 16 held-out synthetic campus queries. This is not real-world accuracy.

| Metric | Development | Final test |
|---|---:|---:|
| Recall@1 | 0.958 | 0.812 |
| Recall@3 | 1.000 | 1.000 |
| Recall@5 | 1.000 | 1.000 |
| MRR | 0.979 | 0.906 |

Eligible queries: 16. Candidates: 32. Top-1 failures: 3. Warm ranking latency: average 0.134 ms, median 0.123 ms, p95 0.198 ms.

## Descriptive challenge slices

| Challenge | Queries | Recall@1 | Recall@3 | Recall@5 | MRR |
|---|---:|---:|---:|---:|---:|
| `ambiguous_description` | 4 | 1.000 | 1.000 | 1.000 | 1.000 |
| `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| `date_gap` | 2 | 0.500 | 1.000 | 1.000 | 0.750 |
| `location_conflict` | 3 | 1.000 | 1.000 | 1.000 | 1.000 |
| `missing_both_images` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| `missing_found_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| `missing_lost_image` | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| `similar_item` | 15 | 0.800 | 1.000 | 1.000 | 0.900 |
