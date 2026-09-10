"""Optional PyTorch sequence model for controlled comparison, not default use."""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover - optional dependency boundary
    raise ImportError("Install the `deep` extra to use sequence models") from exc


class GRUForecaster(nn.Module):
    """Compact GRU with dropout and a scalar SOH/RUL output head."""

    def __init__(self, input_size: int, hidden_size: int = 32, dropout: float = 0.15) -> None:
        super().__init__()
        self.gru = nn.GRU(input_size, hidden_size, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(hidden_size, 1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        encoded, _ = self.gru(inputs)
        return self.head(self.dropout(encoded[:, -1])).squeeze(-1)
