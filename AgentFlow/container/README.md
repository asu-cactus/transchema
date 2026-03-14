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

## 2. Run on CHPC

```bash
cd /path/to/transschema/AgentFlow
chmod +x train/chpc_container_run.sh

# If the SIF is on scratch (recommended):
APPTAINER_IMAGE=/scratch/general/vast/u1592362/AgentFlow_container/transschema-agentflow-cu128.sif \
  bash train/chpc_container_run.sh --smoke_test
```

If you see `FATAL: "python": executable file not found in $PATH`, update to the latest
`train/chpc_container_run.sh` from this repo or run `python3.11` inside the container.

For a real training run, omit `--smoke_test`:

```bash
APPTAINER_IMAGE=/path/to/transschema-agentflow-cu128.sif \
  bash train/chpc_container_run.sh
```

## Notes

- The repo is bind-mounted into the container at `/workspace/transschema`.
- CHPC scratch is bind-mounted so checkpoints, rollouts, and HF cache remain on scratch.
- This path is intended to avoid host-side package drift and host GLIBC / Python-header issues.

