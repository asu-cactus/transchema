# running_scripts/

Sample, runnable invocations of every approach in this repo — TreeMorpher, BAT, MMTU,
SQLMorpher, and the alternate-baseline arms (CoO+Critique / CoO+ReAct / CoT+ReAct) — using
`dmx-gpt-oss-120b` on the GitHub-pipelines benchmark as the worked example, since that's the
model/dataset pair with a complete, real run on this machine.

Each file here is a thin wrapper around the real launcher scripts (at the repo root, in
`BAT/`, `ChatGPTwithSQLscript/`, and `alternate_baselines/`) with the settings actually used
for that run. **Run them from the repo root**, not from inside `running_scripts/`.

## Before running any of these

1. `cd ~/transchema && source env/bin/activate`
2. `dmx-*` models (like the oss-120b example here) need the SSH tunnel to the Azure proxy:
   `ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>`
3. Only ever run ONE of TreeMorpher / an alternate-baseline arm / BAT at a time — they all
   write into the same benchmark case folders and will corrupt each other's output if run
   concurrently. MMTU and SQLMorpher are safe alongside the others (MMTU uses its own sandbox;
   SQLMorpher uses Postgres tables with fixed names, so don't run two SQLMorpher instances at
   once either).
4. Each script prints its own `DRY_RUN=1` preview support where the underlying launcher has
   it — check the launcher's own header comment (`head -40 <script>`) for the full list of
   environment-variable overrides (MAX_JOBS, LENGTHS, CASE_TIMEOUT, RUN_TAG, etc.) before
   changing the model or dataset.

## To reproduce with a different model or dataset

Every script below just sets `MODEL=`/`MODELS=` and, for TreeMorpher, calls the GitHub or
Smart Building v2 variant. Swap the model name (e.g. `dmx-deepseek-v4-pro`, `o4-mini`,
`gpt-4.1-mini`) and/or point at the `_sb_v2_`/`smartbuilding_v2` scripts instead of the
`github_` ones for the other dataset — the underlying launchers are the actual, current ones
used for every model run this session, not a special "sample-only" copy.

## Files

| file | approach | what it reproduces |
|---|---|---|
| `treemorpher_github_oss120b_example.sh` | TreeMorpher (MCTS) | Two-phase run: leaf-stopping on, then a no-leaf-stop retry of whatever phase 1 didn't solve |
| `bat_github_oss120b_example.sh` | BAT | Full 698-case GitHub run, 20 parallel workers |
| `mmtu_github_oss120b_example.sh` | MMTU | One-shot schema-transform baseline, full GitHub coverage |
| `sqlmorpher_github_oss120b_example.sh` | SQLMorpher | ChatGPT+SQL baseline, full GitHub coverage |
| `alternate_baselines_github_oss120b_example.sh` | CoO+Critique / CoO+ReAct / CoT+ReAct | The three arms, run one after another (never in parallel — they share case folders) |
