# Instructions: extract every Python script from run9 MCTS logs

## Goal

For each case in the run9 experiment, read its MCTS log file and pull out
**every unique Python script that appears anywhere in the log** — one script
per LLM turn that produced code (both "Simulate" turns, which write a fresh
pipeline script, and "Critique" turns, which write a corrected one). A single
case log typically contains a few to a few dozen such scripts across all its
MCTS iterations.

## Where the logs are

Two directories, both under the repo root (`~/transchema/`):

```
logs_langraph/rag_det_score_run9_l1_pilot20/        (cases 0-19ish)
logs_langraph/rag_det_score_run9_l1_batch_20to100/   (cases ~20-100)
```

Each contains one subdirectory per case: `cases_c<N>/`, e.g. `cases_c2/`,
`cases_c57/`. Inside that subdirectory is exactly one `.log` file (glob
`cases_c<N>/*.log` — the filename has a timestamp suffix, e.g.
`1_target2_MCTS_20260702_001336.log`). Some cases exist in both directories;
if so, use the actual file present (they shouldn't overlap in case numbers,
but if they do, prefer the newer timestamp).

To get the full case list: list all `cases_c*` subdirectory names in both
dirs and union them (strip the `cases_c` prefix to get the case number).

## Log structure — what to look for

The log is plain text, one logged line at a time, timestamped like:

```
2026-07-02 00:14:08,656 - INFO - <message>
```

Scripts are embedded inside LLM responses following this pattern, in order:

1. A line containing `Query of Type : MCTS <Kind>` — marks the start of one
   LLM turn. `<Kind>` is one of `Expand`, `Simulate`, `Critique`. **Only
   `Simulate` and `Critique` turns ever contain a full pipeline script** —
   skip `Expand` turns, they just pick the next operator, no code.
2. A line containing `Result Recieved :` — marks the start of the LLM's raw
   response text, which continues over the following lines until...
3. A line containing `Cost of the query : {'total_cost': ...}` — marks the
   end of that response.

Everything between the `Result Recieved :` line and the `Cost of the query`
line is the LLM's raw response. Inside that response text, find the **last**
fenced code block of the form:

```
```python
<script text>
```
```

(i.e. a line that is exactly ` ```python ` opens the block — **match this
case-insensitively, some responses use ` ```Python `** — and the next line
that is exactly ` ``` ` closes it). A single response can contain more than
one such block (e.g. it shows "current script" first, then the corrected
one) — always take the **last** one in that response, since that's the
LLM's final answer for that turn.

**Skip a block if:**
- It's empty after stripping whitespace, or
- Its content is literally the placeholder `<corrected code here>` (this
  happens when the LLM's response format wasn't followed correctly — no
  real script here).

## What to record per script

For each extracted script, keep at minimum:
- **case number** (from the `cases_c<N>` directory name)
- **iteration number** — from the most recent `[MCTS Select] Iter <N>:`
  log line *before* the script's `Query of Type` line (iterations are
  monotonically increasing within a case; a new `MCTS Select` line starts a
  new iteration and resets which script "belongs" to it)
- **kind** — `sim` or `critique`, from step 1 above
- **the script text** itself

Optionally, also grab the score assigned to that iteration, if useful for
your downstream analysis — look for a line later in the same iteration:
```
[execute_and_score] Iter <N>: reward=<score> (mode=det_score_value), validation_passed=<bool>, history=[...]
```
(`reward` is the sim score; if a critique followed, there's also a
`[mcts_critique] Iter <N>: score <old> → <new>` line with the post-critique
score.)

## Practical notes

- Read the whole log file at once (they're typically 50KB-500KB, not huge)
  rather than streaming line-by-line if your tooling allows it — simplifies
  tracking "current iteration" and "current query type" as you scan top to
  bottom.
- Process files independently per case — there's no cross-case state.
- A case can have anywhere from a couple scripts (if it terminated in 1-2
  iterations) up to ~80+ (40 iterations × up to 2 scripts each, sim+critique).
- Do not assume every iteration has both a sim and a critique script — some
  iterations only have one or the other depending on how the search branched.

## Existing reference implementation

If your agent has access to this repo, there is already a working parser
that implements exactly this logic — `extract_all_scored_scripts()` in
[analyze_run8_failed_case_scripts.py](../analyze_run8_failed_case_scripts.py)
(lines 39-100+), built on the regexes defined in
[eval_run8_training.py](../eval_run8_training.py) (`RE_QUERY_TYPE`,
`RE_RESULT_RCV`, `RE_COST_LINE`, `RE_SELECT`, `RE_SCORE`,
`_extract_last_code_block`). It returns a list of
`(iteration, kind, script, score)` tuples per log file. Reusing/importing it
is faster and less error-prone than reimplementing the parser from scratch —
only point your agent at the run9 log paths above (it currently defaults to
a different log dir, `LOG_DIR = "logs_langraph/rag_det_score_run8_l1_training"`,
so it'll need that constant changed or the function called directly with an
explicit log file path).
