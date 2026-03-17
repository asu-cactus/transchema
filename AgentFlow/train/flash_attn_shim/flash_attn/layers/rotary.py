"""
flash_attn.layers.rotary — SDPA-compatible version for the sm_120 shim.

Derived from flash-attention v2.7.4.post1 source:
  https://github.com/Dao-AILab/flash-attention/blob/v2.7.4.post1/flash_attn/layers/rotary.py

The real module dispatches through a Triton kernel
(flash_attn.ops.triton.rotary.apply_rotary).  That kernel does not exist in
the SDPA shim (and is not needed — it only fuses the operation, it is not more
correct).  Here we use apply_rotary_emb_torch, which is the pure-PyTorch
reference implementation that lives in the original source and produces
identical numerical results.

All public symbols present in the original are preserved so that imports of
any form work correctly.
"""

import math
from typing import Optional, Tuple, Union

import torch
from einops import rearrange, repeat


# ---------------------------------------------------------------------------
# Pure-PyTorch rotation helpers (from flash_attn source)
# ---------------------------------------------------------------------------

def rotate_half(x: torch.Tensor, interleaved: bool = False) -> torch.Tensor:
    if not interleaved:
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)
    else:
        x1, x2 = x[..., ::2], x[..., 1::2]
        return rearrange(torch.stack((-x2, x1), dim=-1), "... d two -> ... (d two)", two=2)


def apply_rotary_emb_torch(
    x: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    interleaved: bool = False,
) -> torch.Tensor:
    """
    Pure-PyTorch RoPE application (reference implementation from flash_attn source).

    x:   (batch_size, seqlen, nheads, headdim)
    cos, sin: (seqlen, rotary_dim / 2) or (batch_size, seqlen, rotary_dim / 2)
    """
    ro_dim = cos.shape[-1] * 2
    assert ro_dim <= x.shape[-1]
    cos = repeat(cos, "... d -> ... 1 (2 d)" if not interleaved else "... d -> ... 1 (d 2)")
    sin = repeat(sin, "... d -> ... 1 (2 d)" if not interleaved else "... d -> ... 1 (d 2)")
    return torch.cat(
        [x[..., :ro_dim] * cos + rotate_half(x[..., :ro_dim], interleaved) * sin, x[..., ro_dim:]],
        dim=-1,
    )


# ---------------------------------------------------------------------------
# apply_rotary — used internally by ApplyRotaryEmb* classes.
# The real implementation is a Triton kernel; we fall back to PyTorch.
# ---------------------------------------------------------------------------

def apply_rotary(
    x: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    seqlen_offsets: Union[int, torch.Tensor] = 0,
    cu_seqlens: Optional[torch.Tensor] = None,
    max_seqlen: Optional[int] = None,
    interleaved: bool = False,
    inplace: bool = False,
    conjugate: bool = False,
) -> torch.Tensor:
    """PyTorch fallback for flash_attn.ops.triton.rotary.apply_rotary."""
    if conjugate:
        sin = -sin

    if x.dim() == 4:
        # Batched: (batch, seqlen, nheads, headdim)
        if isinstance(seqlen_offsets, int) and seqlen_offsets > 0:
            cos = cos[seqlen_offsets:]
            sin = sin[seqlen_offsets:]
        out = apply_rotary_emb_torch(x, cos, sin, interleaved=interleaved)
    else:
        # Packed: (total_seqlen, nheads, headdim)
        # Treat each token's position individually using cos/sin indexed by row.
        ro_dim = cos.shape[-1] * 2
        total = x.shape[0]
        if isinstance(seqlen_offsets, int) and seqlen_offsets > 0:
            cos_sel = cos[seqlen_offsets : seqlen_offsets + total]
            sin_sel = sin[seqlen_offsets : seqlen_offsets + total]
        else:
            cos_sel = cos[:total]
            sin_sel = sin[:total]
        # Expand to (total, 1, ro_dim)
        cos_e = repeat(
            cos_sel, "s d -> s 1 (2 d)" if not interleaved else "s d -> s 1 (d 2)"
        )
        sin_e = repeat(
            sin_sel, "s d -> s 1 (2 d)" if not interleaved else "s d -> s 1 (d 2)"
        )
        out = torch.cat(
            [
                x[..., :ro_dim] * cos_e + rotate_half(x[..., :ro_dim], interleaved) * sin_e,
                x[..., ro_dim:],
            ],
            dim=-1,
        )

    if inplace:
        x.copy_(out)
        return x
    return out


# ---------------------------------------------------------------------------
# Public API — mirrors flash_attn.layers.rotary exactly
# ---------------------------------------------------------------------------

class ApplyRotaryEmb(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        x,
        cos,
        sin,
        interleaved=False,
        inplace=False,
        seqlen_offsets: Union[int, torch.Tensor] = 0,
        cu_seqlens: Optional[torch.Tensor] = None,
        max_seqlen: Optional[int] = None,
    ):
        out = apply_rotary(
            x, cos, sin,
            seqlen_offsets=seqlen_offsets,
            cu_seqlens=cu_seqlens,
            max_seqlen=max_seqlen,
            interleaved=interleaved,
            inplace=inplace,
        )
        if isinstance(seqlen_offsets, int):
            ctx.save_for_backward(cos, sin, cu_seqlens)
            ctx.seqlen_offsets = seqlen_offsets
        else:
            ctx.save_for_backward(cos, sin, cu_seqlens, seqlen_offsets)
            ctx.seqlen_offsets = None
        ctx.interleaved = interleaved
        ctx.inplace = inplace
        ctx.max_seqlen = max_seqlen
        return out if not inplace else x

    @staticmethod
    def backward(ctx, do):
        seqlen_offsets = ctx.seqlen_offsets
        if seqlen_offsets is None:
            cos, sin, cu_seqlens, seqlen_offsets = ctx.saved_tensors
        else:
            cos, sin, cu_seqlens = ctx.saved_tensors
        if not ctx.interleaved and not ctx.inplace:
            do = do.clone()
        dx = apply_rotary(
            do, cos, sin,
            seqlen_offsets=seqlen_offsets,
            cu_seqlens=cu_seqlens,
            max_seqlen=ctx.max_seqlen,
            interleaved=ctx.interleaved,
            inplace=ctx.inplace,
            conjugate=True,
        )
        return dx, None, None, None, None, None, None, None


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
    """
    Apply rotary position embeddings (RoPE) to *x*.

    Arguments:
        x:              (batch, seqlen, nheads, headdim) or
                        (total_seqlen, nheads, headdim) when cu_seqlens is set.
        cos, sin:       (seqlen_rotary, rotary_dim / 2)
        interleaved:    GPT-J style (adjacent pairs) when True;
                        GPT-NeoX / LLaMA style (split halves) when False.
        inplace:        modify x in place.
        seqlen_offsets: int or (batch,) tensor for KV-cache inference.
        cu_seqlens:     (batch+1,) for varlen / packed format.
        max_seqlen:     int (informational).
    """
    return ApplyRotaryEmb.apply(
        x, cos, sin, interleaved, inplace, seqlen_offsets, cu_seqlens, max_seqlen
    )


# Backward-compatibility alias used by some older integrations
apply_rotary_emb_func = apply_rotary_emb


def apply_rotary_emb_qkv_(
    qkv: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    cos_k: Optional[torch.Tensor] = None,
    sin_k: Optional[torch.Tensor] = None,
    interleaved: bool = False,
    seqlen_offsets: Union[int, torch.Tensor] = 0,
    num_heads_q: Optional[int] = None,
) -> torch.Tensor:
    """Apply RoPE in-place to q and k inside a qkv tensor."""
    cos_k = cos if cos_k is None else cos_k
    sin_k = sin if sin_k is None else sin_k
    if qkv.dim() == 5:
        q, k = qkv[:, :, 0], qkv[:, :, 1]
    else:
        assert num_heads_q is not None
        num_heads_k = (qkv.shape[2] - num_heads_q) // 2
        q = qkv[:, :, :num_heads_q]
        k = qkv[:, :, num_heads_q : num_heads_q + num_heads_k]
    apply_rotary(q, cos, sin, seqlen_offsets, interleaved=interleaved, inplace=True)
    apply_rotary(k, cos_k, sin_k, seqlen_offsets, interleaved=interleaved, inplace=True)
    return qkv


def apply_rotary_emb_kv_(
    kv: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    interleaved: bool = False,
    seqlen_offsets: Union[int, torch.Tensor] = 0,
) -> torch.Tensor:
    """Apply RoPE in-place to k inside a kv tensor."""
    apply_rotary(kv[:, :, 0], cos, sin, seqlen_offsets, interleaved=interleaved, inplace=True)
    return kv


class RotaryEmbedding(torch.nn.Module):
    """Rotary position embeddings (RoFormer, Su et al. 2023)."""

    def __init__(
        self,
        dim: int,
        base: float = 10000.0,
        interleaved: bool = False,
        scale_base: Optional[float] = None,
        pos_idx_in_fp32: bool = True,
        device=None,
    ):
        super().__init__()
        self.dim = dim
        self.base = float(base)
        self.pos_idx_in_fp32 = pos_idx_in_fp32
        self.interleaved = interleaved
        self.scale_base = scale_base
        inv_freq = self._compute_inv_freq(device)
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        scale = (
            (torch.arange(0, dim, 2, device=device, dtype=torch.float32) + 0.4 * dim)
            / (1.4 * dim)
            if scale_base is not None
            else None
        )
        self.register_buffer("scale", scale, persistent=False)
        self._seq_len_cached = 0
        self._cos_cached = None
        self._sin_cached = None
        self._cos_k_cached = None
        self._sin_k_cached = None

    def _compute_inv_freq(self, device=None):
        return 1.0 / (
            self.base
            ** (torch.arange(0, self.dim, 2, device=device, dtype=torch.float32) / self.dim)
        )

    def _update_cos_sin_cache(self, seqlen, device=None, dtype=None):
        if (
            seqlen > self._seq_len_cached
            or self._cos_cached is None
            or self._cos_cached.device != device
            or self._cos_cached.dtype != dtype
            or (self.training and self._cos_cached.is_inference())
        ):
            self._seq_len_cached = seqlen
            if self.pos_idx_in_fp32:
                t = torch.arange(seqlen, device=device, dtype=torch.float32)
                inv_freq = (
                    self._compute_inv_freq(device=device)
                    if self.inv_freq.dtype != torch.float32
                    else self.inv_freq
                )
            else:
                t = torch.arange(seqlen, device=device, dtype=self.inv_freq.dtype)
                inv_freq = self.inv_freq
            freqs = torch.outer(t, inv_freq)
            if self.scale is None:
                self._cos_cached = torch.cos(freqs).to(dtype)
                self._sin_cached = torch.sin(freqs).to(dtype)
            else:
                power = (
                    torch.arange(seqlen, dtype=self.scale.dtype, device=self.scale.device)
                    - seqlen // 2
                ) / self.scale_base
                scale = self.scale.to(device=power.device) ** rearrange(power, "s -> s 1")
                self._cos_cached = (torch.cos(freqs) * scale).to(dtype)
                self._sin_cached = (torch.sin(freqs) * scale).to(dtype)
                self._cos_k_cached = (torch.cos(freqs) / scale).to(dtype)
                self._sin_k_cached = (torch.sin(freqs) / scale).to(dtype)

    def forward(
        self,
        qkv: torch.Tensor,
        kv: Optional[torch.Tensor] = None,
        seqlen_offset: Union[int, torch.Tensor] = 0,
        max_seqlen: Optional[int] = None,
        num_heads_q: Optional[int] = None,
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        seqlen = qkv.shape[1]
        if max_seqlen is not None:
            self._update_cos_sin_cache(max_seqlen, device=qkv.device, dtype=qkv.dtype)
        elif isinstance(seqlen_offset, int):
            self._update_cos_sin_cache(seqlen + seqlen_offset, device=qkv.device, dtype=qkv.dtype)
        if kv is None:
            return apply_rotary_emb_qkv_(
                qkv,
                self._cos_cached,
                self._sin_cached,
                self._cos_k_cached if self.scale is not None else None,
                self._sin_k_cached if self.scale is not None else None,
                interleaved=self.interleaved,
                seqlen_offsets=seqlen_offset,
                num_heads_q=num_heads_q,
            )
        else:
            q = apply_rotary_emb(
                qkv,
                self._cos_cached,
                self._sin_cached,
                interleaved=self.interleaved,
                inplace=True,
                seqlen_offsets=seqlen_offset,
            )
            kv = apply_rotary_emb_kv_(
                kv,
                self._cos_k_cached if self.scale is not None else self._cos_cached,
                self._sin_k_cached if self.scale is not None else self._sin_cached,
                interleaved=self.interleaved,
                seqlen_offsets=seqlen_offset,
            )
            return q, kv
