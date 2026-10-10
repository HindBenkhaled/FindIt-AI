# Validation record

Final validation was completed on Windows with Python 3.12.6. The tested Python package snapshot is in `requirements-lock.txt`; frontend versions are locked by `frontend/package-lock.json`.

## Application checks

- `python -m pytest -q`: backend, API, privacy, matching, cache, benchmark, and split-integrity tests pass.
- `npm run build`: TypeScript checking and the Vite production build pass.
- `npm run test:e2e`: six Chromium journeys cover desktop and mobile navigation, report creation, image upload, E5 + SigLIP ranking, privacy boundaries, claims, responsive layout, and automated WCAG A/AA checks.
- `python -m pip check`: the local Python environment has no broken requirements.
- Public API tests verify that found descriptions, identifying details, sub-locations, image paths, original images, and handover points do not cross the student-facing response boundary.
- Upload tests cover content validation, the 8 MB and 20 MP limits, metadata-removing JPEG re-encoding, replacement, and deletion.

Automated accessibility checks catch common violations but do not replace manual assistive-technology testing. The staff key is a local demonstration mechanism, not production authentication.

## Frozen evaluation

- Development compared MiniLM, BGE-base, and E5-base through the same ranking pipeline; E5-base was selected.
- CLIP, SigLIP, and DINOv2 were compared on fixed COIL-100 exact-object protocols; SigLIP was selected for hard-view performance.
- A 204-combination development search did not improve the original balanced weights.
- The E5 + SigLIP stack, weights, exhaustive retrieval strategy, and scoring-source hashes were frozen before the independent seed-9107 test split was generated.
- Dev/test integrity checks confirm disjoint report IDs, exact descriptions, identifying-detail strings, and image hashes.
- The test generator and evaluator refuse overwrite or rerun.
- The single final run measured Recall@1 **0.8125**, Recall@3 **1.000**, Recall@5 **1.000**, and MRR **0.90625** across 16 queries and 32 candidates, with three top-1 failures.
- No model, weight, example, label, or scoring change followed the held-out result.

These are held-out synthetic-campus results, not real-world accuracy. Procedural benchmark images do not represent clutter, occlusion, lighting, or viewpoint variation in student photographs.

## UI evidence

The screenshots in `docs/screenshots/` use synthetic campus fixtures and show the current **Home**, **Report**, and **Explore** navigation. They cover the report choice and form, match search, privacy-safe found notices, ranked matches, claim verification, and mobile home. Screenshot scores are presentation fixtures rather than evaluation evidence.

React development uses Vite's `/api` proxy. A hosted build would require the same reverse-proxy route. Local runs should remain bound to `127.0.0.1` because authentication, authorization, rate limiting, and university identity integration are outside this portfolio MVP.
