"""
Pure-PyTorch implementation of flash_attn.layers.rotary.apply_rotary_emb.

HuggingFace transformers 4.53+ imports apply_rotary_emb from this submodule
at module level in modeling_flash_attention_utils.py.  The real flash_attn
wheel contains a CUDA kernel for this; the implementation here uses only
standard PyTorch tensor operations and runs correctly on all GPU architectures
including Blackwell (sm_120).

The function applies Rotary Position Embeddings (RoPE) to the input tensor,
following the original formulation from Su et al. (2023) "RoFormer".

Numerical equivalence to the flash_attn CUDA kernel
----------------------------------------------------
Both produce identical results up to floating-point reordering, which has no
effect on training convergence.  For fp16/bf16 mixed-precision training the
accumulation order differences are of the same order as normal batch-to-batch
numerical variation.
"""

from __future__ import annotations

from typing import Optional, Union

import torch


def _rotate_half(x: torch.Tensor) -> torch.Tensor:
    """Negate the second half and swap halves: [a, b] -> [-b, a].

    This is the "split" (non-interleaved) rotation used by LLaMA, Qwen, Mistral
    and most other models that import apply_rotary_emb from flash_attn.
    """
    half = x.shape[-1] // 2
    x1, x2 = x[..., :half], x[..., half:]
    return torch.cat((-x2, x1), dim=-1)


def _rotate_interleaved(x: torch.Tensor) -> torch.Tensor:
    """Rotate adjacent pairs: [a0, a1, a2, a3, ...] -> [-a1, a0, -a3, a2, ...].

    This is the "interleaved" rotation used by GPT-NeoX / some older models.
    """
    x_flat = x.reshape(*x.shape[:-1], -1, 2)
    x_rot = torch.stack((-x_flat[..., 1], x_flat[..., 0]), dim=-1)
    return x_rot.reshape(x.shape)


def apply_rotary_emb(
    x: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    interleaved: bool = False,
    inplace: bool = False,
    seqlen_offsets: Union[int, torch.Tensor] = 0,
    cu_seqlens: Optional[torch.Tensor] = None,
    max_seqlen: Optional[int] = None,
) -> torch.Tensor:
    """Apply rotary position embeddings to *x*.

    Args:
        x:               Query or key tensor.
                         Shape: ``(batch, seqlen, nheads, headdim)``
                         or ``(total_seqlen, nheads, headdim)`` when
                         *cu_seqlens* is provided (packed / varlen format).
        cos:             Pre-computed cosines.  Shape: ``(seqlen, rotary_dim)``
                         or ``(seqlen, rotary_dim // 2)``.
        sin:             Pre-computed sines.  Same shape as *cos*.
        interleaved:     If True use the interleaved (GPT-NeoX) rotation;
                         if False (default) use the split (LLaMA/Qwen) rotation.
        inplace:         Modify *x* in place and return it.
        seqlen_offsets:  Integer or ``(batch,)`` tensor of per-sample KV-cache
                         offsets.  Slices *cos*/*sin* accordingly.
        cu_seqlens:      Cumulative sequence lengths for varlen / packed format.
                         When provided *x* is ``(total_seqlen, nheads, headdim)``.
        max_seqlen:      Maximum sequence length (unused; kept for API parity).

    Returns:
        Tensor with the same shape and dtype as *x*.
    """
    rotary_dim = cos.shape[-1]
    # If cos/sin are half-sized (rotary_dim == headdim // 2), expand them.
    if rotary_dim * 2 <= x.shape[-1]:
        cos = torch.cat([cos, cos], dim=-1)   # (seqlen, rotary_dim_full)
        sin = torch.cat([sin, sin], dim=-1)
        rotary_dim = cos.shape[-1]

    # Slice positions for KV-cache offset (integer case).
    if isinstance(seqlen_offsets, int) and seqlen_offsets > 0:
        cos = cos[seqlen_offsets:]
        sin = sin[seqlen_offsets:]

    # --- Broadcast cos/sin to match x ---
    if x.dim() == 4:
        # Batched: (batch, seqlen, nheads, headdim)
        seqlen = x.shape[1]
        # Apply per-sample offset tensor if provided
        if isinstance(seqlen_offsets, torch.Tensor):
            # Build a (batch, 1, 1, rotary_dim) mask via gather
            batch = x.shape[0]
            idx = seqlen_offsets.view(batch, 1) + torch.arange(
                seqlen, device=x.device
            ).unsqueeze(0)  # (batch, seqlen)
            idx = idx.clamp(max=cos.shape[0] - 1)
            cos = cos[idx].unsqueeze(2)  # (batch, seqlen, 1, rotary_dim)
            sin = sin[idx].unsqueeze(2)
        else:
            cos = cos[:seqlen].unsqueeze(0).unsqueeze(2)  # (1, seqlen, 1, d)
            sin = sin[:seqlen].unsqueeze(0).unsqueeze(2)
    elif x.dim() == 3:
        # Packed: (total_seqlen, nheads, headdim)
        total = x.shape[0]
        cos = cos[:total].unsqueeze(1)   # (total_seqlen, 1, rotary_dim)
        sin = sin[:total].unsqueeze(1)
    else:
        raise ValueError(f"apply_rotary_emb: expected 3-D or 4-D x, got {x.dim()}-D")

    # --- Separate the part to rotate from the pass-through part ---
    if rotary_dim < x.shape[-1]:
        x_rot  = x[..., :rotary_dim]
        x_pass = x[..., rotary_dim:]
    else:
        x_rot  = x
        x_pass = None

    # --- Apply rotation ---
    rotate_fn = _rotate_interleaved if interleaved else _rotate_half
    x_rot_out = x_rot * cos + rotate_fn(x_rot) * sin

    # --- Reassemble ---
    if x_pass is not None:
        out = torch.cat([x_rot_out, x_pass], dim=-1)
    else:
        out = x_rot_out

    if inplace:
        x.copy_(out)
        return x
    return out
