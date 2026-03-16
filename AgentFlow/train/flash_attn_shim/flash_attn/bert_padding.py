"""
Pure-Python reimplementation of flash_attn.bert_padding.

flash_attn.bert_padding contains only tensor-indexing operations — no CUDA
kernels.  This module provides the same API so that:
  - the container sanity check (importlib.import_module("flash_attn.bert_padding"))
    continues to pass even when the flash_attn shim is active on PYTHONPATH.
  - verl's use_remove_padding=True code path keeps working without needing the
    real flash_attn package.

The implementations match the reference in flash_attn/bert_padding.py from
flash-attn 2.x (see https://github.com/Dao-AILab/flash-attention).
"""

from __future__ import annotations

import torch
from typing import Tuple


def unpad_input(
    hidden_states: torch.Tensor,
    attention_mask: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
    """Remove padding tokens from a padded batch of sequences.

    Args:
        hidden_states: ``(batch, seqlen, dim)``
        attention_mask: ``(batch, seqlen)``, 1 for real tokens, 0 for padding.

    Returns:
        hidden_states_unpadded: ``(total_tokens, dim)``
        indices:                ``(total_tokens,)`` flat positions in the batch
        cu_seqlens:             ``(batch + 1,)`` cumulative sequence lengths
        max_seqlen_in_batch:    int
    """
    seqlens = attention_mask.sum(dim=-1, dtype=torch.int32)
    indices = torch.nonzero(attention_mask.flatten(), as_tuple=False).flatten()
    max_seqlen = int(seqlens.max().item())
    cu_seqlens = torch.nn.functional.pad(
        torch.cumsum(seqlens, dim=0, dtype=torch.int32), (1, 0)
    )
    return (
        index_first_axis(
            hidden_states.view(-1, hidden_states.shape[-1]), indices
        ),
        indices,
        cu_seqlens,
        max_seqlen,
    )


def pad_input(
    hidden_states: torch.Tensor,
    indices: torch.Tensor,
    batch: int,
    seqlen: int,
) -> torch.Tensor:
    """Restore padding tokens to a packed sequence tensor.

    Args:
        hidden_states: ``(total_tokens, dim)``
        indices:       ``(total_tokens,)`` from :func:`unpad_input`
        batch:         batch size
        seqlen:        sequence length

    Returns:
        ``(batch, seqlen, dim)`` padded tensor (zeros at padding positions).
    """
    dim = hidden_states.shape[-1]
    output = hidden_states.new_zeros(batch * seqlen, dim)
    output[indices] = hidden_states
    return output.view(batch, seqlen, dim)


def index_first_axis(x: torch.Tensor, indices: torch.Tensor) -> torch.Tensor:
    """Equivalent to ``x[indices]`` — select rows from the first axis."""
    return x[indices]
