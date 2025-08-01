
# Findings Report: Similarity Search Algorithms

## 1. Introduction

This report compares two different similarity search algorithms supported by our chosen vector database, Qdrant. The objective is to understand the trade-offs between search speed (latency) and search accuracy in a practical RAG context and to determine the best approach for a production environment.

## 2. Methodology

### 2.1. Test Environment and Corpus

The test was conducted on a vector database populated with the chunks from the `company_profile.txt` document (sample txt file), which was processed using the `SemanticChunker` strategy. This resulted in a small, targeted dataset of 5-10 vectors. The environment was run locally using Docker for the Qdrant instance.

### 2.2. Test Implementation

A dedicated Python script, `test.py`, was created to perform the experiment. This script used the `qdrant-client` and `sentence-transformers` libraries to:

1. Define a constant test query: `"What programming language is used for the Helios architecture?"`.
2. Convert this query into a vector embedding using the same `all-MiniLM-L6-v2` model used during ingestion.
3. Execute two distinct search operations against the Qdrant collection, measuring the execution time of each.

### 2.3. Search Algorithms

The following two search methods were compared:

* **Algorithm A (Approximate):** **HNSW (Hierarchical Navigable Small World)**. This is Qdrant's default Approximate Nearest Neighbor (ANN) algorithm. The search was performed using the standard `client.search()` method, which leverages the pre-built HNSW index.
* **Algorithm B (Exact):** **Full Scan (Brute-Force)**. This algorithm was executed by calling the `client.search()` method with the `search_params=models.SearchParams(exact=True)` parameter. This forces Qdrant to ignore the HNSW index and compute the distance between the query vector and every vector in the collection.

## 3. Results

The `test.py` script was executed, yielding the following performance metrics. Accuracy was confirmed to be 100% for both methods, as they returned the identical set of results.

| Algorithm   | Search Type        | Avg. Retrieval Latency (ms) | Accuracy |
| :---------- | :----------------- | :-------------------------- | :------- |
| **A** | HNSW (Approximate) | **35.60 ms**          | 100%     |
| **B** | Full Scan (Exact)  | **29.07 ms**          | 100%     |

## 4. Analysis and Conclusion

The results on this small dataset were initially surprising: the **Exact (Full Scan) search was marginally faster than the Approximate (HNSW) search.**

This counter-intuitive latency result can be explained by the overhead of the HNSW indexing algorithm. HNSW achieves its speed on large datasets by building a complex graph that allows it to intelligently navigate to the most relevant region of vectors without checking every single one. However, for a very small number of vectors (under a few hundred), the computational cost of traversing this graph index can be slightly higher than the cost of a simple brute-force comparison against all points. The exact search, while computationally intensive in theory, is very direct on a small scale.

**Recommendation:**
Despite the results on this small-scale test, for any production-grade RAG system intended to scale to thousands or millions of documents, the **HNSW (Approximate) algorithm is still the unequivocal choice**. Its performance benefits grow exponentially with the size of the dataset, whereas the latency of an Exact search increases linearly, quickly becoming a bottleneck. The results of this test highlight an important performance characteristic of vector databases at different scales and confirm that for this project's current scale, either method is functionally acceptable, but HNSW is built for future growth.

---
