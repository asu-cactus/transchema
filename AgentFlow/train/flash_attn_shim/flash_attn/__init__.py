"""
flash_attn compatibility shim for Blackwell GPU (sm_120).

Problem
-------
The PyPI flash_attn wheel (e.g. 2.7.4.post1) is compiled for sm<=90.
Calling its CUDA kernels on a Blackwell GPU (sm_120) produces an unhandled
CUDA error ("no kernel image available") that kills the Ray worker with
SIGSEGV / connection error code 2 — no Python traceback.

Solution
--------
Prepend this directory to PYTHONPATH so Python finds this shim package
instead of the real flash_attn.  The shim's __getattr__ raises ImportError
for the CUDA-backed symbols (flash_attn_func, flash_attn_varlen_func, …),
which is exactly what HuggingFace's is_flash_attn_2_available() catches:

    try:
        from flash_attn import flash_attn_func   # our shim raises ImportError
        ...
        return True
    except ImportError:
        return False                              # HF falls back to SDPA

SDPA (torch.nn.functional.scaled_dot_product_attention) supports sm_120
natively via PyTorch / cuDNN — no extra kernels required.

The bert_padding submodule is provided as a pure-Python submodule so that
the container sanity check and verl's use_remove_padding path work correctly.
"""

__version__ = "2.7.4.post1"

_CUDA_BLOCKED: frozenset = frozenset({
    "flash_attn_func",
    "flash_attn_varlen_func",
    "flash_attn_with_kvcache",
    "flash_attn_qkvpacked_func",
    "flash_attn_kvpacked_func",
    "_flash_attn_forward",
    "_flash_attn_varlen_forward",
    "_flash_attn_backward",
    "_flash_attn_varlen_backward",
    "flash_attn_varlen_qkvpacked_func",
    "flash_attn_varlen_kvpacked_func",
})


def __getattr__(name: str):
    if name in _CUDA_BLOCKED:
        raise ImportError(
            f"flash_attn.{name}: CUDA kernels in the installed flash_attn wheel "
            "are compiled for sm<=90 and do not support the current Blackwell GPU "
            "(sm_120).  This shim prevents the crash.  HuggingFace detects this "
            "ImportError via is_flash_attn_2_available() and falls back to SDPA."
        )
    raise AttributeError(f"module 'flash_attn' has no attribute {name!r}")
