"""Small plotting API shared by notebooks and reports."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes


def set_project_style() -> None:
    """Apply a restrained, accessible plotting style."""

    sns.set_theme(style="whitegrid", context="talk", palette="colorblind")


def plot_soh_trajectories(frame: pd.DataFrame, target: str = "soh_composite_pct") -> Axes:
    """Plot cell-level SOH without hiding between-cell variation."""

    set_project_style()
    _, ax = plt.subplots(figsize=(11, 6))
    sns.lineplot(
        data=frame,
        x="assessment_index",
        y=target,
        hue="cell_id",
        style="cell_id",
        markers=True,
        dashes=False,
        ax=ax,
    )
    ax.axhline(80.0, color="black", linestyle="--", linewidth=1.2, label="80% threshold")
    ax.set(xlabel="Degradation assessment", ylabel="SOH / %", title="Cell-level SOH trajectories")
    return ax
