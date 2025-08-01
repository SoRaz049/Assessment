# Finding Report: Chunking & Embedding Strategies

## 1. Introduction

This report details the evaluation of 2 different text chunking strategies for our RAG system. The goal was to find a strategy that balances ingestion latency with retrieval accuracy, ensuring the RAG agent receives the most relevant context to answer user queries.

## 2. Methodology

### 2.1. Test Corpus

The primary test document was `company_profile.txt`, a sample text file with clear sections and paragraphs. An initial test was also performed on a single-page PDF , which highlighted the initial problems.

### 2.2. Test Configurations

Two primary chunking strategies were implemented and compared:

* **Config A (Baseline):** `RecursiveCharacterTextSplitter` from LangChain. This method splits text based on a hierarchy of separators (`\n\n`, `\n`, ) and a fixed character chunk size (initially 1000, then 500).
* **Config B (Improved):** `SemanticChunker` from LangChain Experimental. This method uses an embedding model (`all-MiniLM-L6-v2`) to find semantic break points between sentences, splitting the text based on changes in topic.

### 2.3. Evaluation

Accuracy was measured qualitatively by observing the agent's ability to answer specific, targeted questions that required retrieving information from distinct sections of the document, including follow-up questions that tested the context.

- **Test Questions:**
  1. "Who founded QuantumLeap AI?"
  2. (Follow-up) "Where are they located?"
  3. "What programming language is used for their core technology?"

## 3. Results

| Configuration | Chunking Strategy | Ingestion Latency | Retrieval Accuracy (Qualitative)                                               | Notes                                                                                                                                                                                      |
| :------------ | :---------------- | :---------------- | :----------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A**   | Recursive (1000)  | Very Fast (~1s)   | **Poor**. Failed on specific follow-up questions.                        | Created 2-3 large, semantically mixed chunks.                                                                                                                                              |
| **A2**  | Recursive (500)   | Very Fast (~1s)   | **Poor**. Marginal improvement, but still failed on follow-up questions. | Chunks were smaller but still lacked semantic coherence.                                                                                                                                   |
| **B**   | Semantic          | Slower (~4-5s)    | **Excellent**. Correctly answered all test and follow-up questions.      | Created semantically pure chunks aligned with the document's topics.<br />The ingestion latency is higher due to the extra computation of the embedding model during the chunking process. |

## 4. Analysis and Conclusion

The initial implementation using `RecursiveCharacterTextSplitter` proved to be fast but unreliable for accurate information retrieval. The chunks created were arbitrary and often mixed multiple unrelated topics, which confused the vector search retriever. Even with smaller chunk sizes, the core problem of lacking semantic awareness persisted.

The transition to `SemanticChunker` yielded a dramatic improvement in retrieval accuracy. By creating chunks based on topic boundaries, it ensured that the context passed to the LLM was highly relevant and clean. This allowed the agent to answer specific and follow-up questions correctly.

**Recommendation:** For a robust, general-purpose RAG system designed to handle diverse documents, the **`SemanticChunker` is the superior choice**, despite its higher ingestion latency. The significant gain in retrieval accuracy justifies the upfront computational cost.

## 5. Potential Future Improvements for Retrieval

While `SemanticChunker` provides a strong baseline, several advanced techniques could further enhance the retrieval quality of this system:

1. **Hybrid Search**: The current system relies solely on semantic (vector) search. For queries containing specific keywords, part numbers, or acronyms, a hybrid approach combining semantic search with traditional keyword search (like BM25) would be more robust. Qdrant has native support for this.
2. **Advanced Embedding Models**: We used the fast `all-MiniLM-L6-v2` model. For higher accuracy, especially on domain-specific documents, a larger and more powerful model like `bge-large-en-v1.5` could be used. This would increase ingestion time and cost but would likely improve the nuance of the semantic search.
3. **Re-ranking Models**: A powerful pattern is to retrieve a larger number of documents initially (e.g., top 10) and then use a more computationally expensive but highly accurate cross-encoder model to re-rank these 10 documents to find the absolute best matches before passing them to the final LLM.
4. **Query Transformations**: For complex queries, the initial user question could be transformed before retrieval. This could involve using an LLM to expand acronyms, decompose a complex question into several sub-questions, or generate hypothetical answers to search for, further improving the chances of finding relevant context.

---
