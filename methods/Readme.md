## Multistep Method

The Multistep Method automates complex data transformations by breaking them into smaller, manageable steps. It guides an LLM to generate precise transformation code in stages, ensuring clarity and correctness.

### Workflow

1. **Operation Classification**
   Analyze source and target schemas (with sample rows) to determine a sequence of high-level operations (e.g., `JOIN`, `FILTER`, `AGGREGATE`).

2. **Code Generation**
   Prompt the LLM with the identified operations and source schema details to produce executable transformation code (SQL or Python).

3. **Intermediate Materialization**
   For pipelines exceeding two operations, materialize intermediate outputs to disk or memory to validate each step before proceeding.

## Critique Method

The Critique Method enhances output accuracy by comparing transformed results against the target and iteratively refining the transformation code based on detected discrepancies.

| Prompt Stage | Context Included                                       |
| ------------ | ------------------------------------------------------ |
| 1            | Target samples + inferred Functional Dependencies (FD) |
| 2            | Stage 1 context + column metadata (types, stats)       |
| 3            | Stage 2 context + anonymized column values             |

### Workflow

1. **Initial Transformation**
   Execute the Multistep Method to obtain a transformed table.

2. **Mismatch Detection**
   Compare the transformed table to the target, checking both schema alignment and sample values.

3. **Iterative Refinement**
   When mismatches are found, issue targeted critique prompts to the LLM to correct errors and regenerate the transformation code.

4. **Re-apply & Validate**
   Run the revised code, recheck for alignment with the target, and repeat until discrepancies are resolved.
