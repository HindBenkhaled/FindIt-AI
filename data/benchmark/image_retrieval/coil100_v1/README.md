# COIL-100 exact-object retrieval benchmark

This benchmark measures whether an image encoder retrieves another view of the same physical object. It does not use category labels for relevance.

The protocol uses all 100 COIL-100 objects. Each object contributes query views at 0° and 180°. The easy gallery contains 5° and 185° views; the hard gallery contains 90° and 270° views. Each setting therefore has 200 queries, 200 gallery images and exactly two relevant gallery images per query. Query files and angles are absent from both galleries.

Recall@K is the fraction of the two relevant views present in the first K results, averaged over queries. Consequently, Recall@1 has a mathematical maximum of 0.5. MRR uses the rank of the first relevant result.

The images come from Columbia University’s Columbia Object Image Library. The official page offers a public download but does not state a standardized license. Treat the files as research/academic data and do not redistribute them. The downloaded files stay under the Git-ignored `data/external/coil100/` directory. See `provenance.json` for the URL, citation, access date and archive source.

COIL-100 has controlled backgrounds, turntable-style views, limited object diversity, older low-resolution imagery, and little clutter or occlusion. It measures controlled same-object viewpoint robustness, not real campus lost-and-found performance.

```powershell
.\.venv\Scripts\python.exe -m scripts.download_coil100
.\.venv\Scripts\python.exe -m scripts.build_coil100_benchmark
.\.venv\Scripts\python.exe -m scripts.evaluate_coil100 --model all
```

## Possible second benchmark

The Washington RGB-D Object Dataset has exact instance identities for 300 household objects and varied camera heights. Its cropped evaluation set is about 643 MB and is restricted to non-commercial research/educational use. It is the lower-effort next benchmark, though its imagery is still turntable-oriented. The full RGB-D release is about 84 GB and is not justified here.

Amazon Berkeley Objects is more modern and includes 8,209 multi-view sequences, but the complete collection is close to 300 GB and requires more metadata/subset engineering. The current AWS registry states CC BY 4.0 after a 2023 license update. A carefully pinned spin-image subset could be valuable later, but it should not be downloaded automatically at this stage.
