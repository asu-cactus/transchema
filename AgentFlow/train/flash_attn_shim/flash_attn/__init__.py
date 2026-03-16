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

    Handles packed (variable-length, padding-free) sequences by temporarily
    padding them to uniform length, running SDPA, then repacking the output.

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

    # Unpack into padded tensors
    q_pad = q.new_zeros(batch, max_seqlen_q, nheads_q, headdim)
    k_pad = k.new_zeros(batch, max_seqlen_k, nheads_k, headdim)
    v_pad = v.new_zeros(batch, max_seqlen_k, nheads_k, headdim)

    for i in range(batch):
        sq = int(cu_seqlens_q[i + 1]) - int(cu_seqlens_q[i])
        sk = int(cu_seqlens_k[i + 1]) - int(cu_seqlens_k[i])
        q_pad[i, :sq] = q[int(cu_seqlens_q[i]):int(cu_seqlens_q[i + 1])]
        k_pad[i, :sk] = k[int(cu_seqlens_k[i]):int(cu_seqlens_k[i + 1])]
        v_pad[i, :sk] = v[int(cu_seqlens_k[i]):int(cu_seqlens_k[i + 1])]

    # Build additive attention bias: -inf at padding positions in the key
    # Shape: (batch, 1, 1, max_seqlen_k) — broadcasts over (batch, nheads, seqlen_q, seqlen_k)
    attn_bias = q.new_zeros(batch, 1, 1, max_seqlen_k)
    for i in range(batch):
        sk = int(cu_seqlens_k[i + 1]) - int(cu_seqlens_k[i])
        if sk < max_seqlen_k:
            attn_bias[i, 0, 0, sk:] = float("-inf")

    if causal:
        # Upper-triangular causal mask (future positions = -inf)
        causal_mask = torch.triu(
            torch.full(
                (max_seqlen_q, max_seqlen_k),
                float("-inf"),
                dtype=q.dtype,
                device=q.device,
            ),
            diagonal=1,
        )
        attn_bias = attn_bias + causal_mask.unsqueeze(0).unsqueeze(0)

    # SDPA: transpose to (batch, nheads, seqlen, headdim)
    q_t = q_pad.transpose(1, 2)
    k_t = k_pad.transpose(1, 2)
    v_t = v_pad.transpose(1, 2)

    # GQA expansion (after transpose: dim=1 is nheads)
    if nheads_q != nheads_k:
        assert nheads_q % nheads_k == 0
        rep = nheads_q // nheads_k
        k_t = k_t.repeat_interleave(rep, dim=1)
        v_t = v_t.repeat_interleave(rep, dim=1)

    out_t = F.scaled_dot_product_attention(
        q_t, k_t, v_t,
        attn_mask=attn_bias,
        dropout_p=dropout_p if torch.is_grad_enabled() else 0.0,
        is_causal=False,  # causal is encoded in attn_bias above
        scale=softmax_scale,
    )

    out_pad = out_t.transpose(1, 2)  # (batch, max_seqlen_q, nheads, headdim)

    # Repack output
    out_chunks = [
        out_pad[i, :int(cu_seqlens_q[i + 1]) - int(cu_seqlens_q[i])]
        for i in range(batch)
    ]
    out = torch.cat(out_chunks, dim=0)

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
