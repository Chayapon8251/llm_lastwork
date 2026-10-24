# Evaluation protocol

`test.json`: 30 retrieval questions, 18 single-source and 12 multi-source. Labels were authored with the corpus by the developer using AI assistance; **not independently human-validated**. This is an initial curated benchmark, not evidence of real-user performance. No class LLM is called by the retrieval evaluation.

`dev.json`: six separate development questions for initial inspection of retrieval and the conservative cosine floor (0.04). `unsupported.json`: six manual negative/unsupported scenarios; not quietly included in recall averages. They are exposed as honest failure examples and are not claimed to pass an automated faithfulness evaluation.

Frozen comparison: character-trigram TF-IDF cosine top-1 (naive named baseline), the **same retriever top-3** (budget control), BM25 top-3, and BM25 + TF-IDF with RRF(60) top-3. All use the same corpus and cosine floor. No synonym rules were fitted on the test set. The top-1 comparison changes context budget, so any improvement against it must not be attributed entirely to hybrid search. Use the top-3 comparison to isolate fusion.

Metrics: macro recall@k, precision@k, MRR truncated to the returned list, and all-relevant coverage. For a missing relevant document, RR=0. We report each system's actual cutoff, not a misleading recall@3 label for the top-1 baseline. Per-query rankings and failures are saved. We do not claim that citation membership proves factual faithfulness.

Run: `python -m scripts.evaluate`. Reproduce metrics from raw committed data. The output includes SHA-256 hashes. The current small test set was inspected once after implementation; treat it as a development benchmark going forward. Collect a fresh, independently annotated held-out set before claiming generalization.
