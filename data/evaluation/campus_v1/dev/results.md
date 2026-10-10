# campus_v1 development results

Synthetic development data only; no final test split and no real photos. Do not report as real-world performance.

Warm-model, warm content-addressed embedding-cache latency around rank_reports only; machine-specific.

| Cohort | Method | Queries | Candidates | Recall@1 | Recall@3 | Recall@5 | MRR | Avg latency (ms) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| image_complete | baseline | 20 | 43 | 0.400 | 1.000 | 1.000 | 0.700 | 18.92 |
| image_complete | text | 20 | 43 | 0.300 | 1.000 | 1.000 | 0.642 | 117.16 |
| image_complete | image | 20 | 43 | 1.000 | 1.000 | 1.000 | 1.000 | 273.06 |
| image_complete | text_image | 20 | 43 | 0.500 | 1.000 | 1.000 | 0.742 | 30.80 |
| image_complete | full | 20 | 43 | 0.600 | 1.000 | 1.000 | 0.800 | 82.39 |
| all_reports | baseline | 24 | 48 | 0.375 | 1.000 | 1.000 | 0.681 | 3.74 |
| all_reports | text | 24 | 48 | 0.333 | 1.000 | 1.000 | 0.660 | 37.77 |
| all_reports | text_image | 24 | 48 | 0.458 | 1.000 | 1.000 | 0.722 | 29.96 |
| all_reports | full | 24 | 48 | 0.542 | 1.000 | 1.000 | 0.771 | 62.61 |

## Results by challenge tag

| Cohort | Method | Challenge | Queries | Recall@1 | Recall@3 | Recall@5 | MRR |
|---|---|---|---:|---:|---:|---:|---:|
| image_complete | baseline | `ambiguous_description` | 5 | 0.400 | 1.000 | 1.000 | 0.700 |
| image_complete | baseline | `category_conflict` | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| image_complete | baseline | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | baseline | `location_conflict` | 4 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | baseline | `similar_item` | 20 | 0.400 | 1.000 | 1.000 | 0.700 |
| image_complete | text | `ambiguous_description` | 5 | 0.400 | 1.000 | 1.000 | 0.667 |
| image_complete | text | `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | text | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | text | `location_conflict` | 4 | 0.500 | 1.000 | 1.000 | 0.750 |
| image_complete | text | `similar_item` | 20 | 0.300 | 1.000 | 1.000 | 0.642 |
| image_complete | image | `ambiguous_description` | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | image | `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | image | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | image | `location_conflict` | 4 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | image | `similar_item` | 20 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | text_image | `ambiguous_description` | 5 | 0.400 | 1.000 | 1.000 | 0.667 |
| image_complete | text_image | `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | text_image | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | text_image | `location_conflict` | 4 | 0.500 | 1.000 | 1.000 | 0.750 |
| image_complete | text_image | `similar_item` | 20 | 0.500 | 1.000 | 1.000 | 0.742 |
| image_complete | full | `ambiguous_description` | 5 | 0.600 | 1.000 | 1.000 | 0.800 |
| image_complete | full | `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | full | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | full | `location_conflict` | 4 | 1.000 | 1.000 | 1.000 | 1.000 |
| image_complete | full | `similar_item` | 20 | 0.600 | 1.000 | 1.000 | 0.800 |
| all_reports | baseline | `ambiguous_description` | 6 | 0.333 | 1.000 | 1.000 | 0.639 |
| all_reports | baseline | `category_conflict` | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| all_reports | baseline | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | baseline | `location_conflict` | 4 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | baseline | `missing_both_images` | 2 | 0.000 | 1.000 | 1.000 | 0.417 |
| all_reports | baseline | `missing_found_image` | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| all_reports | baseline | `missing_lost_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | baseline | `similar_item` | 23 | 0.391 | 1.000 | 1.000 | 0.696 |
| all_reports | text | `ambiguous_description` | 6 | 0.333 | 1.000 | 1.000 | 0.639 |
| all_reports | text | `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | text | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | text | `location_conflict` | 4 | 0.500 | 1.000 | 1.000 | 0.750 |
| all_reports | text | `missing_both_images` | 2 | 0.000 | 1.000 | 1.000 | 0.500 |
| all_reports | text | `missing_found_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | text | `missing_lost_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | text | `similar_item` | 23 | 0.348 | 1.000 | 1.000 | 0.667 |
| all_reports | text_image | `ambiguous_description` | 6 | 0.333 | 1.000 | 1.000 | 0.639 |
| all_reports | text_image | `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | text_image | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | text_image | `location_conflict` | 4 | 0.500 | 1.000 | 1.000 | 0.750 |
| all_reports | text_image | `missing_both_images` | 2 | 0.000 | 1.000 | 1.000 | 0.500 |
| all_reports | text_image | `missing_found_image` | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| all_reports | text_image | `missing_lost_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | text_image | `similar_item` | 23 | 0.478 | 1.000 | 1.000 | 0.732 |
| all_reports | full | `ambiguous_description` | 6 | 0.500 | 1.000 | 1.000 | 0.750 |
| all_reports | full | `category_conflict` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | full | `date_gap` | 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | full | `location_conflict` | 4 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | full | `missing_both_images` | 2 | 0.000 | 1.000 | 1.000 | 0.500 |
| all_reports | full | `missing_found_image` | 1 | 0.000 | 1.000 | 1.000 | 0.500 |
| all_reports | full | `missing_lost_image` | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| all_reports | full | `similar_item` | 23 | 0.565 | 1.000 | 1.000 | 0.783 |

## Notable Recall@1 failures

- **baseline**: 15 of 24 queries missed at rank 1. See `results.json` for IDs, ranks and tags.
  - Query 1001: top candidate 3001; relevant 2001 ranked 2 (`similar_item, ambiguous_description`).
  - Query 1003: top candidate 3003; relevant 2003 ranked 2 (`similar_item`).
  - Query 1004: top candidate 3004; relevant 2004 ranked 2 (`similar_item, ambiguous_description`).
  - Query 1005: top candidate 3005; relevant 2005 ranked 2 (`similar_item`).
  - Query 1006: top candidate 3006; relevant 2006 ranked 2 (`similar_item, category_conflict`).
- **text**: 16 of 24 queries missed at rank 1. See `results.json` for IDs, ranks and tags.
  - Query 1001: top candidate 3001; relevant 2001 ranked 2 (`similar_item, ambiguous_description`).
  - Query 1003: top candidate 3003; relevant 2003 ranked 2 (`similar_item`).
  - Query 1004: top candidate 3004; relevant 2004 ranked 3 (`similar_item, ambiguous_description`).
  - Query 1005: top candidate 3005; relevant 2005 ranked 2 (`similar_item`).
  - Query 1007: top candidate 3007; relevant 2007 ranked 2 (`similar_item`).
- **text_image**: 13 of 24 queries missed at rank 1. See `results.json` for IDs, ranks and tags.
  - Query 1001: top candidate 3001; relevant 2001 ranked 2 (`similar_item, ambiguous_description`).
  - Query 1003: top candidate 3003; relevant 2003 ranked 2 (`similar_item`).
  - Query 1004: top candidate 3004; relevant 2004 ranked 3 (`similar_item, ambiguous_description`).
  - Query 1005: top candidate 3005; relevant 2005 ranked 2 (`similar_item`).
  - Query 1008: top candidate 3008; relevant 2008 ranked 2 (`similar_item`).
- **full**: 11 of 24 queries missed at rank 1. See `results.json` for IDs, ranks and tags.
  - Query 1001: top candidate 3001; relevant 2001 ranked 2 (`similar_item, ambiguous_description`).
  - Query 1003: top candidate 3003; relevant 2003 ranked 2 (`similar_item`).
  - Query 1004: top candidate 3004; relevant 2004 ranked 2 (`similar_item, ambiguous_description`).
  - Query 1005: top candidate 3005; relevant 2005 ranked 2 (`similar_item`).
  - Query 1008: top candidate 3008; relevant 2008 ranked 2 (`similar_item`).
