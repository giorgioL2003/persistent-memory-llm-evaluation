#!/usr/bin/env python3
"""Genera il grafico percentuale di RQ1 per la presentazione.

Il grafico mostra solo percentuali: non espone il numero totale di domande e
non modifica i risultati sperimentali. I valori provengono dalla tabella delle
metriche aggregate in ``pilot/pilot_summary.md``.

Esecuzione dalla cartella del progetto:
    .venv-grafici/bin/python scripts/plot_rq1_presentation.py
"""

import os
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "pilot" / "pilot_summary.md"
OUTPUT_DIR = PROJECT / "risultati_tesi" / "RQ1"
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT / ".matplotlib-cache"))

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    raise SystemExit(
        "Matplotlib manca in questo Python. Usa .venv-grafici/bin/python."
    )


CONDITIONS = ("C0", "C1", "C2")
LABELS = ("Senza\nmemoria", "Memoria\nlocale", "Memoria\ncondivisa")
METRICS = {
    "Reachability Rate": "Informazioni disponibili",
    "Complete Answer Rate": "Risposte complete corrette",
}
COLORS = {
    "Reachability Rate": "#C66526",
    "Complete Answer Rate": "#3070AD",
}


def load_percentages(path=SOURCE):
    """Legge le percentuali C0/C1/C2 dalla tabella aggregata di RQ1."""
    text = path.read_text(encoding="utf-8")
    values = {}
    for metric in METRICS:
        match = re.search(
            rf"^\| {re.escape(metric)} \|(.+?)\|$",
            text,
            flags=re.MULTILINE,
        )
        if match is None:
            raise ValueError(f"Metrica non trovata in {path}: {metric}")
        cells = [cell.strip() for cell in match.group(1).split("|")]
        percentages = []
        for cell in cells:
            percentage = re.search(r"([0-9]+(?:\.[0-9]+)?)%", cell)
            if percentage is None:
                raise ValueError(f"Percentuale non trovata in: {cell}")
            percentages.append(float(percentage.group(1)))
        if len(percentages) != len(CONDITIONS):
            raise ValueError(
                f"{metric}: attesi {len(CONDITIONS)} valori, trovati "
                f"{len(percentages)}"
            )
        values[metric] = percentages
    return values


def add_labels(ax, bars, values):
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            max(value + 2.2, 2.2),
            f"{value:.0f}%",
            ha="center",
            va="bottom",
            fontsize=17,
            fontweight="semibold",
            color="#111827",
        )


def main():
    values = load_percentages()
    x = np.arange(len(CONDITIONS))
    width = 0.33

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Aptos", "Arial", "DejaVu Sans"],
        "font.size": 15,
    })
    fig, ax = plt.subplots(figsize=(10.8, 5.8), facecolor="white")

    available = values["Reachability Rate"]
    correct = values["Complete Answer Rate"]
    bars_available = ax.bar(
        x - width / 2,
        available,
        width,
        color=COLORS["Reachability Rate"],
        label=METRICS["Reachability Rate"],
        zorder=3,
    )
    bars_correct = ax.bar(
        x + width / 2,
        correct,
        width,
        color=COLORS["Complete Answer Rate"],
        label=METRICS["Complete Answer Rate"],
        zorder=3,
    )

    add_labels(ax, bars_available, available)
    add_labels(ax, bars_correct, correct)

    ax.set_xticks(x, LABELS, fontsize=17, fontweight="semibold")
    ax.set_ylim(0, 106)
    ax.set_yticks(range(0, 101, 20), [f"{value}%" for value in range(0, 101, 20)])
    ax.set_ylabel("Percentuale", fontsize=16)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.9, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#9CA3AF")
    ax.tick_params(axis="y", labelsize=14, colors="#374151")
    ax.tick_params(axis="x", length=0, pad=10)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=2,
        frameon=False,
        fontsize=14,
    )

    fig.subplots_adjust(left=0.10, right=0.98, top=0.84, bottom=0.20)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        OUTPUT_DIR / "grafico_rq1_percentuali.png",
        dpi=300,
        facecolor="white",
        bbox_inches="tight",
    )
    fig.savefig(
        OUTPUT_DIR / "grafico_rq1_percentuali.svg",
        facecolor="white",
        bbox_inches="tight",
    )
    print(OUTPUT_DIR / "grafico_rq1_percentuali.png")
    print(OUTPUT_DIR / "grafico_rq1_percentuali.svg")


if __name__ == "__main__":
    main()
