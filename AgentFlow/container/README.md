# CHPC Container Path

## 1. Build the image

This is the Blackwell-first reset path.

The container now starts from an NGC PyTorch base and treats the GPU stack as a
coherent unit instead of trying to patch an older CUDA Ubuntu image:

- NGC PyTorch base image
- bundled CUDA / torch from that base
- `xformers` built from source
- `vllm` `v0.9.2` built from source against the base torch
- `verl` layered on top
- `flash-attn` Python package installed with CUDA build skipped so
  `flash_attn.bert_padding` is available to all worker processes

This is intentionally different from the earlier path. The old wheel-based stack
kept failing on Blackwell with `CUDA error: no kernel image is available for execution on the device`.

### Option A: Apptainer on CHPC

If CHPC allows `apptainer build` for your account:

```bash
cd /path/to/transschema
mkdir -p /scratch/general/vast/u1592362/AgentFlow_container
apptainer build /scratch/general/vast/u1592362/AgentFlow_container/transschema-agentflow-cu128.sif AgentFlow/container/apptainer.def
```

Note: the NGC base image may require access to `nvcr.io`. If the build fails
while pulling the base image, use Docker on a machine where you can authenticate
to NGC and then convert/import the resulting image for CHPC.

### Option B: Build Docker elsewhere, run Apptainer on CHPC

```bash
cd /path/to/transschema
docker build -f AgentFlow/container/Dockerfile.chpc -t transschema-agentflow:cu128 .
```

Then convert/import to a `.sif` using your preferred workflow.

## 2. Bootstrap the runtime layer

The scratch runtime layer is still useful, but it is now only for lightweight
Python-only dependencies that should not trigger a full image rebuild.

```bash
cd /path/to/transschema
chmod +x AgentFlow/train/chpc_bootstrap_env.sh AgentFlow/train/chpc_container_run.sh

APPTAINER_IMAGE=/scratch/general/vast/u1592362/AgentFlow_container/transschema-agentflow-cu128.sif \
  bash AgentFlow/train/chpc_bootstrap_env.sh
```

This creates a fresh versioned runtime env on scratch, updates the stable
symlink `AgentFlow_runtime_venv_current`, records a `pip freeze`, and verifies
that both `torch` and `flash_attn.bert_padding` import cleanly.

The bootstrap script no longer assumes Python 3.11 specifically; it uses
whatever Python is provided by the base container.

## 3. Run on CHPC

```bash
cd /path/to/transschema

APPTAINER_IMAGE=/scratch/general/vast/u1592362/AgentFlow_container/transschema-agentflow-cu128.sif \
  bash AgentFlow/train/chpc_container_run.sh --smoke_test
```

The launcher now:

- discovers the runtime venv if present
- injects its `site-packages` into `PYTHONPATH`
- forces Ray workers to use the same interpreter via `RAY_PYTHON_EXECUTABLE`
- validates imports before training starts

For a real training run, omit `--smoke_test`.

## Notes

- The repo is bind-mounted into the container at `/workspace/transschema`.
- CHPC scratch is bind-mounted so checkpoints, rollouts, and HF cache remain on scratch.
- Rebuild the SIF for heavy stack changes like CUDA, torch, vLLM, verl, xformers, or apt packages.
- Use `AgentFlow/train/chpc_runtime_requirements.txt` plus `chpc_bootstrap_env.sh` for lightweight Python-only dependency changes.

