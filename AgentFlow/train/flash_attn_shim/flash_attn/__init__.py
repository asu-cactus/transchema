"""
flash_attn compatibility shim for Blackwell GPU (sm_120).

Problem
-------
The PyPI flash_attn wheel (e.g. 2.7.4.post1) has CUDA kernels compiled only
for sm<=90.  On a Blackwell GPU (sm_120) the kernel launch returns
"no kernel image available", which manifests as an unhandled CUDA error that
kills the Ray worker with exit code None / SIGSEGV — no Python traceback.

Additionally, HuggingFace transformers 4.53+ imports flash_attn_func at MODULE
LEVEL (not inside try/except) in modeling_flash_attention_utils.py, so raising
ImportError from flash_attn_func breaks the entire module import chain and
prevents verl's WorkerDict actor from loading at all.

Solution
--------
This shim provides SDPA-backed (torch.nn.functional.scaled_dot_product_attention)
implementations of every flash_attn symbol that HuggingFace / verl import.
SDPA is natively compiled for all GPU architectures including sm_120.

Place the parent directory of this package on PYTHONPATH BEFORE the system
site-packages so Python resolves "flash_attn" to this shim first:

    PYTHONPATH=/path/to/flash_attn_shim:$PYTHONPATH

How it works
------------
1. is_flash_attn_2_available() in transformers succeeds (flash_attn_func IS
   importable from this shim), so HF selects attn_implementation="flash_attention_2".
2. When the model's attention forward actually runs, it calls this shim's
   flash_attn_func, which delegates to F.scaled_dot_product_attention on the
   GPU — no sm_120-specific kernel needed.
3. bert_padding (pure Python) is re-exported from the submodule for verl's
   use_remove_padding feature.
"""

from __future__ import annotations

__version__ = "2.7.4.post1"

import torch
import torch.nn.functional as F
from typing import Optional, Tuple


# ---------------------------------------------------------------------------
# Standard (padded) attention
# flash_attn convention: q/k/v are (batch, seqlen, nheads, headdim)
# PyTorch SDPA convention: (batch, nheads, seqlen, headdim)
# ---------------------------------------------------------------------------

def flash_attn_func(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    dropout_p: float = 0.0,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    window_size: Tuple[int, int] = (-1, -1),
    alibi_slopes=None,
    deterministic: bool = False,
    return_attn_probs: bool = False,
):
    """SDPA-backed replacement for flash_attn.flash_attn_func.

    Input/output tensors follow flash_attn convention:
        q, k, v : (batch, seqlen, nheads, headdim)
        output  : (batch, seqlen, nheads, headdim)
    """
    # (batch, seqlen, nheads, headdim) → (batch, nheads, seqlen, headdim)
    q = q.transpose(1, 2)
    k = k.transpose(1, 2)
    v = v.transpose(1, 2)

    # GQA: if k/v have fewer heads than q, expand them
    n_heads_q = q.shape[1]
    n_heads_k = k.shape[1]
    if n_heads_q != n_heads_k:
        assert n_heads_q % n_heads_k == 0, (
            f"GQA requires n_heads_q ({n_heads_q}) divisible by n_heads_kv ({n_heads_k})"
        )
        rep = n_heads_q // n_heads_k
        k = k.repeat_interleave(rep, dim=1)
        v = v.repeat_interleave(rep, dim=1)

    out = F.scaled_dot_product_attention(
        q, k, v,
        dropout_p=dropout_p if torch.is_grad_enabled() else 0.0,
        is_causal=causal,
        scale=softmax_scale,
    )

    # (batch, nheads, seqlen, headdim) → (batch, seqlen, nheads, headdim)
    out = out.transpose(1, 2)

    if return_attn_probs:
        return out, None, None
    return out


# ---------------------------------------------------------------------------
# Variable-length (packed) attention
# flash_attn convention: q/k/v are (total_tokens, nheads, headdim)
# ---------------------------------------------------------------------------

def flash_attn_varlen_func(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    cu_seqlens_q: torch.Tensor,
    cu_seqlens_k: torch.Tensor,
    max_seqlen_q: int,
    max_seqlen_k: int,
    dropout_p: float = 0.0,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    window_size: Tuple[int, int] = (-1, -1),
    alibi_slopes=None,
    deterministic: bool = False,
    return_attn_probs: bool = False,
    block_table=None,
):
    """SDPA-backed replacement for flash_attn.flash_attn_varlen_func.

    Processes each sequence in the batch independently so that SDPA's native
    ``is_causal`` flag handles causal masking without allocating an explicit
    O(seq_len²) mask matrix.

    Memory complexity: O(seq_len × nheads × headdim) per sequence, constant
    in the number of sequences.  The previous pad-then-mask approach allocated
    a (max_seqlen_q, max_seqlen_k) causal mask (~355 MB at seq_len=13312) and
    broadcast it to (batch, 1, max_seqlen_q, max_seqlen_k) (~710 MB) on every
    Transformer layer call, causing GPU OOM during compute_log_prob.

    Inputs:
        q, k, v      : (total_tokens, nheads, headdim)
        cu_seqlens_q : (batch+1,) cumulative q-sequence lengths
        cu_seqlens_k : (batch+1,) cumulative k-sequence lengths
    Output:
        (total_tokens, nheads, headdim)
    """
    batch = cu_seqlens_q.shape[0] - 1
    nheads_q = q.shape[1]
    headdim = q.shape[2]
    nheads_k = k.shape[1]
    rep = nheads_q // nheads_k if nheads_q != nheads_k else 1

    if batch == 0:
        out = q.new_zeros(0, nheads_q, headdim)
        return (out, None, None) if return_attn_probs else out

    chunks: list[torch.Tensor] = []
    for i in range(batch):
        q_start = int(cu_seqlens_q[i])
        q_end   = int(cu_seqlens_q[i + 1])
        k_start = int(cu_seqlens_k[i])
        k_end   = int(cu_seqlens_k[i + 1])

        # Slice this sequence: (seqlen, nheads, headdim)
        qi = q[q_start:q_end]
        ki = k[k_start:k_end]
        vi = v[k_start:k_end]

        # SDPA expects (batch, nheads, seqlen, headdim)
        qi = qi.unsqueeze(0).transpose(1, 2)   # (1, nheads_q, sq, headdim)
        ki = ki.unsqueeze(0).transpose(1, 2)   # (1, nheads_k, sk, headdim)
        vi = vi.unsqueeze(0).transpose(1, 2)

        # GQA: expand k/v heads to match q heads
        if rep > 1:
            ki = ki.repeat_interleave(rep, dim=1)
            vi = vi.repeat_interleave(rep, dim=1)

        # SDPA handles causal masking internally — no explicit mask matrix.
        # is_causal=True with no attn_mask is equivalent to flash_attn's causal
        # flag and requires zero additional memory beyond the output tensor.
        oi = F.scaled_dot_product_attention(
            qi, ki, vi,
            dropout_p=dropout_p if torch.is_grad_enabled() else 0.0,
            is_causal=causal,
            scale=softmax_scale,
        )

        # (1, nheads_q, sq, headdim) → (sq, nheads_q, headdim)
        chunks.append(oi.squeeze(0).transpose(0, 1))

    out = torch.cat(chunks, dim=0)

    if return_attn_probs:
        return out, None, None
    return out


# ---------------------------------------------------------------------------
# KV-cache attention (inference only — not needed for training)
# ---------------------------------------------------------------------------

def flash_attn_with_kvcache(
    q,
    k_cache,
    v_cache,
    k=None,
    v=None,
    rotary_cos=None,
    rotary_sin=None,
    cache_seqlens=None,
    cache_batch_idx=None,
    cache_leftpad=None,
    block_table=None,
    softmax_scale=None,
    causal=False,
    window_size=(-1, -1),
    softcap=0.0,
    rotary_interleaved=True,
    alibi_slopes=None,
    num_splits=0,
    return_softmax_lse=False,
):
    """Stub for inference KV-cache attention (not used during training)."""
    raise NotImplementedError(
        "flash_attn_with_kvcache is not implemented in the sm_120 compatibility shim. "
        "This function is only needed for inference; training uses flash_attn_func "
        "or flash_attn_varlen_func, which are SDPA-backed in this shim."
    )


# ---------------------------------------------------------------------------
# QKV-packed variants (less common; provide wrappers)
# ---------------------------------------------------------------------------

def flash_attn_qkvpacked_func(
    qkv,
    dropout_p=0.0,
    softmax_scale=None,
    causal=False,
    window_size=(-1, -1),
    alibi_slopes=None,
    deterministic=False,
    return_attn_probs=False,
):
    """qkv: (batch, seqlen, 3, nheads, headdim)"""
    q, k, v = qkv.unbind(dim=2)
    return flash_attn_func(
        q, k, v,
        dropout_p=dropout_p,
        softmax_scale=softmax_scale,
        causal=causal,
        window_size=window_size,
        alibi_slopes=alibi_slopes,
        deterministic=deterministic,
        return_attn_probs=return_attn_probs,
    )


def flash_attn_kvpacked_func(
    q,
    kv,
    dropout_p=0.0,
    softmax_scale=None,
    causal=False,
    window_size=(-1, -1),
    alibi_slopes=None,
    deterministic=False,
    return_attn_probs=False,
):
    """q: (batch, seqlen, nheads, headdim); kv: (batch, seqlen, 2, nheads, headdim)"""
    k, v = kv.unbind(dim=2)
    return flash_attn_func(
        q, k, v,
        dropout_p=dropout_p,
        softmax_scale=softmax_scale,
        causal=causal,
        window_size=window_size,
        alibi_slopes=alibi_slopes,
        deterministic=deterministic,
        return_attn_probs=return_attn_probs,
    )
