# COIL-100 image-encoder comparison

Exact physical-object retrieval; model loading and embedding cost are separate from cached cosine retrieval.

## Easy

| Model | Recall@1 | Recall@3 | Recall@5 | MRR | Avg ms | Median ms | P95 ms | Dim | Embed s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| clip | 0.500 | 0.910 | 0.932 | 1.000 | 0.056 | 0.042 | 0.057 | 512 | 32.64 |
| siglip | 0.500 | 0.938 | 0.965 | 1.000 | 0.093 | 0.034 | 0.120 | 768 | 145.70 |
| dinov2 | 0.500 | 0.953 | 0.983 | 1.000 | 0.105 | 0.054 | 0.106 | 768 | 161.31 |

## Hard

| Model | Recall@1 | Recall@3 | Recall@5 | MRR | Avg ms | Median ms | P95 ms | Dim | Embed s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| clip | 0.398 | 0.800 | 0.868 | 0.850 | 0.042 | 0.041 | 0.053 | 512 | 32.64 |
| siglip | 0.435 | 0.863 | 0.922 | 0.908 | 0.044 | 0.040 | 0.067 | 768 | 145.70 |
| dinov2 | 0.422 | 0.823 | 0.890 | 0.890 | 0.053 | 0.050 | 0.072 | 768 | 161.31 |

## Representative hard failures

- CLIP misses 41 of 200 queries at rank 1, including toy car object 8, which it confuses with other toy cars.
- SigLIP misses 26 of 200 at rank 1. Object 8 remains difficult, but its relevant view rises from CLIP rank 5 to rank 3.
- DINOv2 misses 31 of 200 at rank 1. Side/rear views of object 9 lose their identifying label and resemble other cylindrical containers.
- Wooden object 12 becomes an ambiguous block silhouette at 90°/270° and is confused with other untextured wooden shapes.

COIL-100 uses controlled black backgrounds, turntable views and older 128 px imagery. These results do not establish performance in cluttered or occluded campus scenes.
