# CHPC Container Path

## 1. Build the image

### Option A: Apptainer on CHPC

If CHPC allows `apptainer build` for your account:

```bash
cd /path/to/transschema

# Build (optionally to scratch to avoid filling home/uufs)
mkdir -p /scratch/general/vast/u1592362/AgentFlow_container
apptainer build /scratch/general/vast/u1592362/AgentFlow_container/transschema-agentflow-cu128.sif AgentFlow/container/apptainer.def
```

If you built the SIF inside the repo (e.g. `AgentFlow/container/transschema-agentflow-cu128.sif`), move it to scratch:

```bash
mkdir -p /scratch/general/vast/u1592362/AgentFlow_container
mv AgentFlow/container/transschema-agentflow-cu128.sif /scratch/general/vast/u1592362/AgentFlow_container/
```

### Option B: Build Docker elsewhere, run Apptainer on CHPC

Build on a Linux machine with Docker:

```bash
cd /path/to/transschema
docker build -f AgentFlow/container/Dockerfile.chpc -t transschema-agentflow:cu128 .
```

Then convert/import to a `.sif` for CHPC using your preferred workflow.

## 2. Bootstrap the fast runtime layer

For lightweight Python dependency changes, use a scratch virtualenv layered on
top of the base SIF instead of rebuilding the image:

```bash
cd /path/to/transschema
chmod +x AgentFlow/train/chpc_bootstrap_env.sh AgentFlow/train/chpc_container_run.sh

APPTAINER_IMAGE=/scratch/general/vast/u1592362/AgentFlow_container/transschema-agentflow-cu128.sif \
  bash AgentFlow/train/chpc_bootstrap_env.sh
```

This installs the pinned packages listed in
`AgentFlow/train/chpc_runtime_requirements.txt` into a scratch virtualenv and
records a `pip freeze` manifest alongside it.

Re-run the bootstrap script whenever you change
`AgentFlow/train/chpc_runtime_requirements.txt`.

If you created the runtime venv with an older version of the bootstrap script,
just rerun it. The script now recreates the venv automatically if it was built
without system site-packages.

## 3. Run on CHPC

```bash
cd /path/to/transschema

# If the SIF is on scratch (recommended):
APPTAINER_IMAGE=/scratch/general/vast/u1592362/AgentFlow_container/transschema-agentflow-cu128.sif \
  bash AgentFlow/train/chpc_container_run.sh --smoke_test
```

If you see `FATAL: "python": executable file not found in $PATH`, update to the latest
`train/chpc_container_run.sh` from this repo or run `python3.11` inside the container.
The launcher now also runs a fast in-container import sanity check before starting training,
so ABI/package issues fail immediately instead of after a long startup.

If you do not want online Weights & Biases logging on CHPC, leave `WANDB_API_KEY` unset;
the launcher will default to `WANDB_MODE=offline`.

Do not add `AgentFlow/agentflow` directly to `PYTHONPATH`; that path contains
`types.py`, which can shadow Python's standard-library `types` module.

For a real training run, omit `--smoke_test`:

```bash
APPTAINER_IMAGE=/path/to/transschema-agentflow-cu128.sif \
  bash AgentFlow/train/chpc_container_run.sh
```

## Notes

- The repo is bind-mounted into the container at `/workspace/transschema`.
- CHPC scratch is bind-mounted so checkpoints, rollouts, and HF cache remain on scratch.
- Rebuild the SIF only for heavy stack changes like CUDA, torch, vLLM, verl, flash-attn, or apt packages.
- Use `AgentFlow/train/chpc_runtime_requirements.txt` plus `chpc_bootstrap_env.sh` for lightweight Python-only dependency changes.
- This path is intended to avoid host-side package drift and host GLIBC / Python-header issues.

