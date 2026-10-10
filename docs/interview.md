# FindIt AI: concise interview refresher

**What did you build?** A privacy-aware campus lost-and-found retrieval system: a React frontend submits reports to FastAPI, SQLite stores them, pretrained encoders represent text/images, and a weighted ranker returns privacy-safe candidates with signal-level explanations and claim verification.

**What is an embedding?** A numeric vector that represents meaning or visual content. Similar inputs tend to have nearby vectors in that model's learned space.

**Why E5-base?** A controlled development comparison tested MiniLM, BGE-base and E5-base through the same ranking pipeline. E5-base ranked best and was frozen before held-out evaluation. This is evidence on a small synthetic benchmark, not a universal model claim.

**What is cosine similarity?** The dot product divided by the product of vector lengths. It measures direction rather than magnitude. With unit-normalized vectors, cosine is their dot product. This project clips negative cosine values to zero for its ranking components.

**Why SigLIP?** CLIP, SigLIP and DINOv2 were compared on exact same-object retrieval across COIL-100 viewpoints. SigLIP was strongest on the hard split. FindIt uses it for image-to-image similarity and combines that score with separate E5 text similarity and contextual signals.

**How are scores combined?** A configurable weighted average of text, image, location, time and category. No classifier is trained, and the result is not a probability. Component distributions differ, so the weights and thresholds need validation on real data.

**How do missing images work?** Image similarity is `None`, not zero. Remove its weight and divide by the sum of the remaining weights. A missing observation should not behave like observed evidence of a bad match. Missingness can still affect comparability between candidates.

**Why a baseline?** A keyword-only method shows what simple word overlap can do. A separate contextual baseline adds location/date/category, helping distinguish the value of context from the value of pretrained embeddings.

**Why Recall@K?** Users inspect a short list. Recall@K measures whether correct matches are present in that list. With one relevant candidate per query, it equals the fraction of queries whose match appears in the first K positions.

**What is MRR?** Average `1 / rank` of the first relevant match. It rewards placing the correct result near the top. Missing results contribute zero.

**Why FastAPI and Pydantic?** FastAPI separates HTTP request handling from the UI and generates API docs. Pydantic validates and serializes structured inputs/outputs, catching invalid reports at the boundary.

**Why SQLite and SQLAlchemy?** SQLite is a persistent SQL database with no separate database server. SQLAlchemy maps Python objects to rows and manages queries/transactions; each request has a short-lived session. PostgreSQL would be appropriate for more concurrent writers.

**Why cache models and embeddings?** Loading model weights for each request would be slow. A process-level cache keeps model objects alive; a disk cache avoids re-encoding unchanged content.

**How do you avoid evaluation leakage?** Development data was used for encoder selection and weight tuning. The chosen E5+SigLIP stack, weights and scoring source hashes were frozen before generating the separate seed-9107 test split. Test files were hashed, evaluated once, and locked against reruns. The lower held-out Recall@1 of 0.8125 was reported without tuning.

**What would change at scale?** Batch encoding, vector retrieval for candidate selection, a production SQL database, managed object storage, access control and monitoring. Keep contextual reranking after retrieval. Measure latency and retrieval quality before adding infrastructure.

**What is the biggest limitation?** The measured dataset is small and synthetic, and the images are procedural fixtures. High scores on it cannot establish effectiveness with real lost-item photos or prove ownership.

**A short demonstration:** Open a seeded AirPods query, compare keyword-only with full ranking, explain the components, then choose the imageless water bottle and show redistributed weights. Finish with the measured results table and its limitations.
