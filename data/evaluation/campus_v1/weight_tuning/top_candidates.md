# campus_v1 candidate-stack weight tuning

Development-only constrained grid: 204 combinations. Text `intfloat/e5-base-v2`; image `google/siglip-base-patch16-224`.

| Candidate | Text | Image | Location | Time | Category | Recall@1 | MRR | Failures | Worsened tags |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Current weights | 0.35 | 0.30 | 0.15 | 0.10 | 0.10 | 0.958 | 0.979 | 1 | none |
| Top 1 | 0.35 | 0.30 | 0.15 | 0.10 | 0.10 | 0.958 | 0.979 | 1 | none |
| Top 2 | 0.30 | 0.30 | 0.15 | 0.10 | 0.15 | 0.958 | 0.979 | 1 | none |
| Top 3 | 0.30 | 0.30 | 0.15 | 0.15 | 0.10 | 0.958 | 0.979 | 1 | none |
| Top 4 | 0.30 | 0.35 | 0.15 | 0.10 | 0.10 | 0.958 | 0.979 | 1 | none |
| Top 5 | 0.35 | 0.25 | 0.15 | 0.10 | 0.15 | 0.958 | 0.979 | 1 | none |
| Top 6 | 0.35 | 0.25 | 0.15 | 0.15 | 0.10 | 0.958 | 0.979 | 1 | none |
| Top 7 | 0.35 | 0.30 | 0.10 | 0.10 | 0.15 | 0.958 | 0.979 | 1 | none |
| Top 8 | 0.35 | 0.30 | 0.10 | 0.15 | 0.10 | 0.958 | 0.979 | 1 | none |
| Top 9 | 0.35 | 0.35 | 0.10 | 0.10 | 0.10 | 0.958 | 0.979 | 1 | none |
| Top 10 | 0.35 | 0.30 | 0.15 | 0.05 | 0.15 | 0.958 | 0.979 | 1 | none |

## Selected balanced candidate

`{"category": 0.1, "image": 0.3, "location": 0.15, "text": 0.35, "time": 0.1}`

Recall@1 0.958; MRR 0.979; 1 top-1 failures.

## Per-tag baseline versus selected

| Challenge | Queries | Baseline R@1 | Selected R@1 | Baseline MRR | Selected MRR |
|---|---:|---:|---:|---:|---:|
| `ambiguous_description` | 6 | 0.833 | 0.833 | 0.917 | 0.917 |
| `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| `location_conflict` | 4 | 1.000 | 1.000 | 1.000 | 1.000 |
| `missing_both_images` | 2 | 0.500 | 0.500 | 0.750 | 0.750 |
| `missing_found_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| `missing_lost_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| `similar_item` | 23 | 1.000 | 1.000 | 1.000 | 1.000 |

## Remaining selected-candidate failures

- Query 1023 (Navy umbrella): ranked 3023 first instead of 2023 (relevant rank 2); tags `ambiguous_description, missing_both_images`.
  The top candidate scored 0.8828 versus 0.8624. Components (top / relevant): text 0.9281 / 0.8873, image None / None, location 1.0000 / 1.0000, time 0.9311 / 0.9311, category 0.5000 / 0.5000.

The scratch/mark, backpack, location-conflict, date-gap, and single-missing-image cases are correct at rank 1 under both the untuned baseline and selected candidate. The remaining umbrella has no image on either side; all contextual components tie, so its slightly higher wrong-candidate text similarity decides the order.
