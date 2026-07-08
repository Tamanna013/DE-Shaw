# TestLens Commit Analyzer

Computes deterministic commit-to-test correlation signals used by the Failure Analyzer.

## Correlation Algorithm
Instead of blindly throwing commits at an LLM, this module pre-computes a strict mathematical `composite_score` for every candidate commit in the failure window. The AI Reasoning Engine then uses this score as deterministic grounding evidence.

The score is a weighted composite of three independent signals:

1. **File Overlap Score (50%)**: What fraction of the stack-trace frames are touched by this commit?
   - **Critical detail**: Frames are not treated equally. A commit touching a file at the *top* of the stack trace (where the exception actually originated) is weighted mathematically higher (using a `1/(index+1)` decay) than a commit touching a file deep in the framework roots.
2. **Proximity Score (20%)**: How close is this commit to the test failure?
   - Computed as `1 / (1 + distance * 0.1)`. A commit exactly at HEAD scores 1.0; a commit 10 SHAs ago scores 0.5.
3. **Historical Score (30%)**: Does this test have a history of breaking when these specific files are changed?
   - Queried against a materialized `commit_test_correlations` aggregate table, which is periodically updated by a batch job (`ComputeHistoricalCorrelationBaselineUseCase`) that mines past resolved AI failure reports.

## Configurable Weights
The weighting constants (`WEIGHT_FILE_OVERLAP = 0.5`, etc.) are isolated at the top of the module, enabling easy A/B testing and tuning of the algorithm's sensitivity.
