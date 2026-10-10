# FindIt campus_v1 benchmark

`campus_v1` is a fully synthetic exact-pair retrieval benchmark. Development contains 24 lost queries, 24 relevant found reports and 24 query-specific hard negatives. The frozen seed-9107 test split contains 16 lost queries, 16 relevant found reports and 16 hard negatives.

Development data supported model selection and weight tuning. The E5-base + SigLIP stack and existing weights were frozen before test generation. Test reports, qrels and every test image are protected by hashes in `test/manifest.json`; the generator and final evaluator refuse overwrite or rerun.

The test split uses separate IDs, descriptions, identifying details, image files, procedural templates and seed. Integrity tests enforce those boundaries. Test metrics are final documentation only and must never be used for tuning.

Both splits use simple procedural images and authored campus reports. They do not measure real university deployment accuracy, cluttered-photo robustness, identity verification, or ownership proof.
