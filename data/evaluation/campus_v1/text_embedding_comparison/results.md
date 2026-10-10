# campus_v1 text-embedding comparison

Raw drop-in text encoders; identical report text, candidates, rank_reports pipeline, image model and weights. No E5/BGE-specific prefixes.

Warm-model, warm content-addressed embedding-cache latency around rank_reports only; machine-specific.

## Overall results

| Cohort | Method | Encoder | Queries | Candidates | Recall@1 | Recall@3 | Recall@5 | MRR | Avg ms | Median ms | P95 ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| image_complete | text | minilm | 20 | 43 | 0.300 | 1.000 | 1.000 | 0.642 | 10.40 | 10.31 | 11.54 |
| image_complete | full | minilm | 20 | 43 | 0.600 | 1.000 | 1.000 | 0.800 | 24.82 | 24.34 | 26.18 |
| all_reports | text | minilm | 24 | 48 | 0.333 | 1.000 | 1.000 | 0.660 | 36.59 | 36.62 | 40.07 |
| all_reports | full | minilm | 24 | 48 | 0.542 | 1.000 | 1.000 | 0.771 | 77.06 | 83.04 | 91.35 |
| image_complete | text | bge-base | 20 | 43 | 0.500 | 1.000 | 1.000 | 0.750 | 42.28 | 41.88 | 49.53 |
| image_complete | full | bge-base | 20 | 43 | 0.850 | 1.000 | 1.000 | 0.925 | 71.65 | 69.77 | 84.30 |
| all_reports | text | bge-base | 24 | 48 | 0.458 | 1.000 | 1.000 | 0.729 | 31.32 | 27.40 | 54.30 |
| all_reports | full | bge-base | 24 | 48 | 0.750 | 1.000 | 1.000 | 0.875 | 73.99 | 72.28 | 106.40 |
| image_complete | text | e5-base | 20 | 43 | 0.550 | 1.000 | 1.000 | 0.775 | 43.75 | 42.23 | 52.85 |
| image_complete | full | e5-base | 20 | 43 | 0.950 | 1.000 | 1.000 | 0.975 | 71.06 | 73.00 | 83.88 |
| all_reports | text | e5-base | 24 | 48 | 0.583 | 1.000 | 1.000 | 0.792 | 29.81 | 26.91 | 47.27 |
| all_reports | full | e5-base | 24 | 48 | 0.917 | 1.000 | 1.000 | 0.958 | 71.76 | 75.03 | 85.81 |

## Challenge-tag changes versus MiniLM

Positive values improved and negative values worsened. Zero means unchanged.

| Cohort | Method | Encoder | Challenge | Queries | Recall@1 | Δ Recall@1 | MRR | Δ MRR |
|---|---|---|---|---:|---:|---:|---:|---:|
| image_complete | text | minilm | `ambiguous_description` | 5 | 0.400 | +0.000 | 0.667 | +0.000 |
| image_complete | text | minilm | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | text | minilm | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | text | minilm | `location_conflict` | 4 | 0.500 | +0.000 | 0.750 | +0.000 |
| image_complete | text | minilm | `similar_item` | 20 | 0.300 | +0.000 | 0.642 | +0.000 |
| image_complete | full | minilm | `ambiguous_description` | 5 | 0.600 | +0.000 | 0.800 | +0.000 |
| image_complete | full | minilm | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | minilm | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | minilm | `location_conflict` | 4 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | minilm | `similar_item` | 20 | 0.600 | +0.000 | 0.800 | +0.000 |
| all_reports | text | minilm | `ambiguous_description` | 6 | 0.333 | +0.000 | 0.639 | +0.000 |
| all_reports | text | minilm | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | minilm | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | minilm | `location_conflict` | 4 | 0.500 | +0.000 | 0.750 | +0.000 |
| all_reports | text | minilm | `missing_both_images` | 2 | 0.000 | +0.000 | 0.500 | +0.000 |
| all_reports | text | minilm | `missing_found_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | minilm | `missing_lost_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | minilm | `similar_item` | 23 | 0.348 | +0.000 | 0.667 | +0.000 |
| all_reports | full | minilm | `ambiguous_description` | 6 | 0.500 | +0.000 | 0.750 | +0.000 |
| all_reports | full | minilm | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | minilm | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | minilm | `location_conflict` | 4 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | minilm | `missing_both_images` | 2 | 0.000 | +0.000 | 0.500 | +0.000 |
| all_reports | full | minilm | `missing_found_image` | 1 | 0.000 | +0.000 | 0.500 | +0.000 |
| all_reports | full | minilm | `missing_lost_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | minilm | `similar_item` | 23 | 0.565 | +0.000 | 0.783 | +0.000 |
| image_complete | text | bge-base | `ambiguous_description` | 5 | 0.600 | +0.200 | 0.800 | +0.133 |
| image_complete | text | bge-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | text | bge-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | text | bge-base | `location_conflict` | 4 | 0.500 | +0.000 | 0.750 | +0.000 |
| image_complete | text | bge-base | `similar_item` | 20 | 0.500 | +0.200 | 0.750 | +0.108 |
| image_complete | full | bge-base | `ambiguous_description` | 5 | 1.000 | +0.400 | 1.000 | +0.200 |
| image_complete | full | bge-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | bge-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | bge-base | `location_conflict` | 4 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | bge-base | `similar_item` | 20 | 0.850 | +0.250 | 0.925 | +0.125 |
| all_reports | text | bge-base | `ambiguous_description` | 6 | 0.500 | +0.167 | 0.750 | +0.111 |
| all_reports | text | bge-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | bge-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | bge-base | `location_conflict` | 4 | 0.500 | +0.000 | 0.750 | +0.000 |
| all_reports | text | bge-base | `missing_both_images` | 2 | 0.000 | +0.000 | 0.500 | +0.000 |
| all_reports | text | bge-base | `missing_found_image` | 1 | 0.000 | -1.000 | 0.500 | -0.500 |
| all_reports | text | bge-base | `missing_lost_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | bge-base | `similar_item` | 23 | 0.478 | +0.130 | 0.739 | +0.072 |
| all_reports | full | bge-base | `ambiguous_description` | 6 | 0.833 | +0.333 | 0.917 | +0.167 |
| all_reports | full | bge-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | bge-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | bge-base | `location_conflict` | 4 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | bge-base | `missing_both_images` | 2 | 0.000 | +0.000 | 0.500 | +0.000 |
| all_reports | full | bge-base | `missing_found_image` | 1 | 0.000 | +0.000 | 0.500 | +0.000 |
| all_reports | full | bge-base | `missing_lost_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | bge-base | `similar_item` | 23 | 0.783 | +0.217 | 0.891 | +0.109 |
| image_complete | text | e5-base | `ambiguous_description` | 5 | 0.600 | +0.200 | 0.800 | +0.133 |
| image_complete | text | e5-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | text | e5-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | text | e5-base | `location_conflict` | 4 | 0.250 | -0.250 | 0.625 | -0.125 |
| image_complete | text | e5-base | `similar_item` | 20 | 0.550 | +0.250 | 0.775 | +0.133 |
| image_complete | full | e5-base | `ambiguous_description` | 5 | 1.000 | +0.400 | 1.000 | +0.200 |
| image_complete | full | e5-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | e5-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | e5-base | `location_conflict` | 4 | 1.000 | +0.000 | 1.000 | +0.000 |
| image_complete | full | e5-base | `similar_item` | 20 | 0.950 | +0.350 | 0.975 | +0.175 |
| all_reports | text | e5-base | `ambiguous_description` | 6 | 0.500 | +0.167 | 0.750 | +0.111 |
| all_reports | text | e5-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | e5-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | e5-base | `location_conflict` | 4 | 0.250 | -0.250 | 0.625 | -0.125 |
| all_reports | text | e5-base | `missing_both_images` | 2 | 0.500 | +0.500 | 0.750 | +0.250 |
| all_reports | text | e5-base | `missing_found_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | e5-base | `missing_lost_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | text | e5-base | `similar_item` | 23 | 0.609 | +0.261 | 0.804 | +0.138 |
| all_reports | full | e5-base | `ambiguous_description` | 6 | 0.833 | +0.333 | 0.917 | +0.167 |
| all_reports | full | e5-base | `category_conflict` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | e5-base | `date_gap` | 2 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | e5-base | `location_conflict` | 4 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | e5-base | `missing_both_images` | 2 | 0.500 | +0.500 | 0.750 | +0.250 |
| all_reports | full | e5-base | `missing_found_image` | 1 | 1.000 | +1.000 | 1.000 | +0.500 |
| all_reports | full | e5-base | `missing_lost_image` | 1 | 1.000 | +0.000 | 1.000 | +0.000 |
| all_reports | full | e5-base | `similar_item` | 23 | 0.957 | +0.391 | 0.978 | +0.196 |
