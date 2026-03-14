# CHPC Container Path

This is the paper-safe path for running DataMorpher RL fine-tuning on CHPC:

- real `torch==2.7.0+cu128`
- real `vllm==0.9.2`
- real `verl==0.5.0`
- real `flash-attn` built inside the container
- no local `flash_attn` shim

## 1. Build the image

### Option A: Apptainer on CHPC

If CHPC allows `apptainer build` for your account:

```bash
cd /path/to/transschema
apptainer build transschema-agentflow-cu128.sif AgentFlow/container/apptainer.def
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
cd /uufs/chpc.utah.edu/common/home/u1592362/Downloads/transschema/AgentFlow
chmod +x train/chpc_container_run.sh

APPTAINER_IMAGE=/path/to/transschema-agentflow-cu128.sif \
  bash train/chpc_container_run.sh --smoke_test
```

For a real training run, omit `--smoke_test`:

```bash
APPTAINER_IMAGE=/path/to/transschema-agentflow-cu128.sif \
  bash train/chpc_container_run.sh
```

## Notes

- The repo is bind-mounted into the container at `/workspace/transschema`.
- CHPC scratch is bind-mounted so checkpoints, rollouts, and HF cache remain on scratch.
- This path is intended to avoid host-side package drift and host GLIBC / Python-header issues.

