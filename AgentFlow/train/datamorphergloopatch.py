"""
datamorphergloopatch.py — loaded at Python startup via gloo_patch.pth

Forces torch.distributed.init_process_group to use the Gloo backend
instead of NCCL for all processes in this job.

Background: veRL's colocated FSDP resource pool runs two workers in
separate processes on different physical GPUs (cudaDev 0 and 1).
NCCL 2.25 treats each as a separate node (nNodes=2, localRanks=1)
because they hold different GPU devices.  In nNodes=2 mode NCCL spawns
proxy threads that call cudaSetDevice + cudaMemcpy for CPU staging.
Those threads have uninitialised CUDA contexts and fail with
"Cuda failure 1 'invalid argument'" in enqueue.cc.

Gloo handles GPU tensors via host-memory staging over TCP, requires no
CUDA IPC or proxy threads, and is fully functional for FSDP on two GPUs
communicating over loopback.
"""
import os


def _install():
    try:
        import torch.distributed.distributed_c10d as _c10d
        import torch.distributed as _td

        _orig = _c10d.init_process_group

        def _gloo_only(*args, **kwargs):
            # Pin CUDA device to LOCAL_RANK/RANK so allocations land on the
            # correct GPU before the process group initialises.
            _lr = os.environ.get("LOCAL_RANK") or os.environ.get("RANK")
            if _lr is not None and str(_lr).isdigit():
                try:
                    import torch as _t
                    _t.cuda.set_device(int(_lr))
                except Exception:
                    pass
            # Drop positional backend arg if present; force Gloo via kwarg.
            if args and isinstance(args[0], str):
                args = args[1:]
            kwargs["backend"] = "gloo"
            return _orig(*args, **kwargs)

        _c10d.init_process_group = _gloo_only
        _td.init_process_group = _gloo_only
    except Exception:
        pass


_install()
