#!/usr/bin/env python3
"""
Diagnostic: check what the ref-policy Ray worker environment looks like.
Run inside the container:

  APPTAINER_IMAGE=.../transschema-agentflow-cu128.sif \
    bash AgentFlow/train/chpc_container_run.sh  \
    --diag_only   # (or paste equivalent apptainer exec command)

Or standalone inside the container shell:
  python3 AgentFlow/train/diag_ref_worker.py
"""
import os, sys

sep = "-" * 60

print(sep)
print("=== sys.path (first 10) ===")
for p in sys.path[:10]:
    print(" ", p)

print(sep)
print("=== PYTHONPATH env var ===")
print(os.environ.get("PYTHONPATH", "(not set)"))

print(sep)
print("=== TORCHDYNAMO_DISABLE ===")
print(os.environ.get("TORCHDYNAMO_DISABLE", "(not set)"))

print(sep)
print("=== flash_attn import ===")
try:
    import flash_attn
    print(f"  version : {flash_attn.__version__}")
    print(f"  location: {flash_attn.__file__}")
    is_shim = "flash_attn_shim" in flash_attn.__file__
    print(f"  is shim : {is_shim}")
except Exception as e:
    print(f"  FAILED  : {e}")

print(sep)
print("=== flash_attn.layers.rotary ===")
try:
    from flash_attn.layers.rotary import apply_rotary_emb
    print(f"  OK: {apply_rotary_emb}")
except Exception as e:
    print(f"  FAILED: {e}")

print(sep)
print("=== verl ===")
try:
    import verl
    print(f"  version : {getattr(verl, '__version__', 'unknown')}")
    print(f"  location: {verl.__file__}")
except Exception as e:
    print(f"  FAILED: {e}")

print(sep)
print("=== torch ===")
try:
    import torch
    print(f"  version   : {torch.__version__}")
    print(f"  CUDA avail: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  device    : {torch.cuda.get_device_name(0)}")
        print(f"  sm        : {torch.cuda.get_device_capability(0)}")
    import torch._dynamo
    print(f"  dynamo.disable: {torch._dynamo.config.disable}")
except Exception as e:
    print(f"  error: {e}")

print(sep)
print("=== compute_ref_log_prob source snippet ===")
try:
    import inspect
    import verl.workers.fsdp_workers as fw
    src, lineno = inspect.getsourcelines(fw.ActorRolloutRefWorker.compute_ref_log_prob)
    print(f"  starts at line {lineno}")
    print("".join(src[:30]))
except Exception as e:
    print(f"  FAILED: {e}")

print(sep)
print("=== vllm importability ===")
try:
    import vllm
    print(f"  OK: {vllm.__version__}  from {vllm.__file__}")
except Exception as e:
    print(f"  FAILED (expected for ref worker): {e}")

print(sep)
print("=== Ray worker logs (if Ray is running) ===")
import glob
for pat in ["/tmp/ray/session_latest/logs/worker-*.err",
            "/tmp/ray/*/logs/worker-*.err"]:
    files = sorted(glob.glob(pat), key=os.path.getmtime, reverse=True)
    if files:
        print(f"  Most recent: {files[0]}")
        try:
            with open(files[0]) as f:
                tail = f.read()[-3000:]
            print(tail)
        except Exception as e:
            print(f"  Could not read: {e}")
        break
else:
    print("  No Ray worker logs found (Ray may not be running).")
