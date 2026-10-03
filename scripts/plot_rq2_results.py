#!/usr/bin/env python3
"""Genera i grafici delle tre metriche conclusive di RQ2.

Esecuzione dalla cartella del progetto:
    .venv-grafici/bin/python scripts/plot_rq2_results.py --all

Per impostazione predefinita ricalcola Recall@k, Exact Match dei fatti e
Correct Abstention Rate dalle annotazioni definitive e salva i PNG in
``risultati_tesi/RQ2``. L'opzione ``--variant`` conserva la precedente vista
delle risposte complete per la successiva prova sul budget. Nessuna chiamata
al modello e nessuna modifica ai giudizi.
"""

import argparse
import json
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
THESIS_OUT = PROJECT / "risultati_tesi" / "RQ2"
EVALUATIONS = {
    scenario: PROJECT / "RACCOLTA_RISULTATI" / scenario /
    f"valutazioni_{scenario.lower()}.jsonl"
    for scenario in ("SC02", "SC03", "SC04", "SC05")
}
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT / ".matplotlib-cache"))

try:
    # Lascia a PyCharm/Matplotlib la scelta del backend per mostrare il grafico.
    import matplotlib.pyplot as plt
except ImportError:
    raise SystemExit(
        "Matplotlib manca in questo Python. Usa .venv-grafici/bin/python oppure "
        "installa la dipendenza con: python -m pip install matplotlib"
    )

# Da PyCharm: cambia questa riga e premi Run.
SCENARIO = "SC05"  # SC02, SC03, SC04 oppure SC05
MODES = {
    "SC02": ("T", "F", "FULL_HISTORY"),
    "SC03": ("F", "U", "FULL_HISTORY"),
    "SC04": ("T", "U", "G", "FULL_HISTORY"),
    "SC05": ("T", "U", "GER", "FULL_HISTORY"),
}
LABELS = {
    "T": "Turn-level RAG",
    "F": "Fact-Based RAG",
    "U": "Memoria con\naggiornamenti",
    "G": "Memoria basata\nsu grafi",
    "GER": "Memoria\ngerarchica",
    "FULL_HISTORY": "Cronologia completa\n(controllo diagnostico)",
}
# Ogni architettura mantiene lo stesso colore in tutti gli scenari.
COLORS = {
    "T": "#0072B2",           # blu
    "F": "#E69F00",           # arancione
    "U": "#009E73",           # verde
    "G": "#CC79A7",           # viola
    "GER": "#D55E00",         # vermiglio
    "FULL_HISTORY": "#C62828", # rosso
}

METRICS = (
    ("recall_at_k", "Recall@k"),
    ("exact_match", "Exact Match\ndei fatti"),
    ("correct_abstention", "Correct Abstention\nRate"),
)


def parse_fraction(value):
    """Restituisce numeratore e denominatore di una frazione ``n/d``."""
    numerator, denominator = value.split("/", 1)
    return int(numerator), int(denominator)


def load_thesis_metrics(paths=EVALUATIONS):
    """Ricalcola le metriche dalle annotazioni definitive di RQ2.

    Recall@k e' la copertura micro dei fatti obbligatori nel contesto: la somma
    dei fatti presenti divisa per la somma dei fatti richiesti. Il valore di k
    e' determinato, domanda per domanda, dagli elementi che entrano nel budget
    di 200 token. FULL_HISTORY non esegue retrieval e resta non applicabile.

    Exact Match dei fatti conta le risposte complete e supportate fra quelle
    per cui l'oracle richiede una risposta. Correct Abstention Rate conta le
    astensioni corrette fra quelle richieste dall'oracle.
    """
    values = {}
    for scenario, path in paths.items():
        rows = [json.loads(line) for line in path.read_text(
            encoding="utf-8").splitlines() if line.strip()]
        for mode in MODES[scenario]:
            mode_rows = [row for row in rows if row["mode"] == mode]
            if len(mode_rows) != 7:
                raise ValueError(
                    f"{scenario}/{mode}: attese 7 annotazioni, trovate "
                    f"{len(mode_rows)}"
                )

            answer_rows = [row for row in mode_rows
                           if row["expected_behavior"] != "Astensione"]
            abstention_rows = [row for row in mode_rows
                               if row["expected_behavior"] == "Astensione"]
            exact_n = sum(bool(row["counts_as_complete_and_supported"])
                          for row in answer_rows)
            abstention_n = sum(row["answer_class"] == "astensione corretta"
                               for row in abstention_rows)

            values[scenario, mode, "exact_match"] = (
                exact_n, len(answer_rows)
            )
            values[scenario, mode, "correct_abstention"] = (
                abstention_n, len(abstention_rows)
            )

            if mode == "FULL_HISTORY":
                values[scenario, mode, "recall_at_k"] = None
                continue

            coverage = [parse_fraction(row["rq2_fact_coverage_in_context"])
                        for row in mode_rows
                        if row["rq2_fact_coverage_in_context"] is not None]
            recall_n = sum(numerator for numerator, _ in coverage)
            recall_d = sum(denominator for _, denominator in coverage)
            if recall_d == 0:
                raise ValueError(f"{scenario}/{mode}: Recall@k senza fatti")
            values[scenario, mode, "recall_at_k"] = (recall_n, recall_d)
    return values


def draw_metrics_scenario(ax, scenario, values):
    modes = MODES[scenario]
    metric_positions = list(range(len(METRICS)))
    width = 0.18 if len(modes) == 4 else 0.22
    center = (len(modes) - 1) / 2

    for mode_index, mode in enumerate(modes):
        offset = (mode_index - center) * width
        positions = [position + offset for position in metric_positions]
        heights = []
        applicable = []
        for metric, _ in METRICS:
            fraction = values[scenario, mode, metric]
            if fraction is None:
                heights.append(0)
                applicable.append(False)
            else:
                numerator, denominator = fraction
                heights.append(100 * numerator / denominator)
                applicable.append(True)

        bars = ax.bar(
            positions,
            heights,
            width=width * 0.88,
            color=COLORS[mode],
            label=LABELS[mode].replace("\n", " "),
            zorder=3,
        )
        for bar, metric, is_applicable in zip(bars, METRICS, applicable):
            metric_name = metric[0]
            if not is_applicable:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    2,
                    "n.a.",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color=COLORS[mode],
                    fontweight="bold",
                )
                continue
            numerator, denominator = values[scenario, mode, metric_name]
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 2,
                f"{numerator}/{denominator}",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

    ax.set_xticks(metric_positions, [label for _, label in METRICS])
    ax.set_ylim(0, 112)
    ax.set_yticks(range(0, 101, 20), [f"{value}%" for value in range(0, 101, 20)])
    ax.set_ylabel("Valore della metrica")
    ax.grid(axis="y", color="#E5E7EB", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=len(modes),
        frameon=False,
        fontsize=9.5,
    )


def decorate_metrics(fig):
    fig.subplots_adjust(left=0.09, right=0.98, top=0.84, bottom=0.14)


def draw_variant_scenario(ax, scenario, values):
    """Mantiene la vista storica della variante sperimentale separata."""
    modes = MODES[scenario]
    positions = [i + (0.5 if mode == "FULL_HISTORY" else 0)
                 for i, mode in enumerate(modes)]
    counts = [int(values[scenario, mode]["complete_e_supportate"].split("/")[0])
              for mode in modes]
    totals = [int(values[scenario, mode]["n_risposte"]) for mode in modes]
    colors = [COLORS[mode] for mode in modes]
    ax.bar(positions, counts, width=0.6, color=colors, zorder=3)
    for x, count, total in zip(positions, counts, totals):
        ax.text(x, count + 0.12, f"{count}/{total}", ha="center", va="bottom",
                fontsize=13, fontweight="bold")
    ax.axvline((positions[-2] + positions[-1]) / 2,
               color="#B2B8BF", linestyle="--")
    ax.set_xticks(positions, [LABELS[mode] for mode in modes])
    ax.set_ylim(0, 7)
    ax.set_yticks(range(8))
    ax.set_ylabel("Risposte complete e supportate")
    ax.set_xlabel("Architettura / controllo diagnostico", labelpad=12)
    ax.grid(axis="y", color="#E5E7EB", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    title = f"{scenario} — Budget di 200 token" if scenario == "SC05" else scenario
    ax.set_title(title, pad=18)


def decorate_variant(fig):
    fig.subplots_adjust(left=0.1, right=0.97, top=0.87, bottom=0.22)


def save(fig, folder, name, extensions=("png", "svg")):
    for extension in extensions:
        path = folder / f"{name}.{extension}"
        fig.savefig(path, dpi=300, facecolor="white")
        print(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        help="cartella di destinazione delle immagini")
    parser.add_argument("--scenario", choices=tuple(MODES), default=SCENARIO)
    parser.add_argument("--all", action="store_true",
                        help="genera in una volta tutti e quattro gli scenari")
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--thesis",
        action="store_true",
        help="calcola le tre metriche definitive (comportamento predefinito)",
    )
    source.add_argument(
        "--variant",
        action="store_true",
        help="usa la successiva prova sul budget e la sua cartella separata",
    )
    parser.add_argument("--show", action="store_true",
                        help="mostra anche le figure in una finestra interattiva")
    args = parser.parse_args()
    if args.scenario not in MODES:
        parser.error("SCENARIO deve essere SC02, SC03, SC04 oppure SC05")

    # 1. La fonte definitiva e' il comportamento predefinito. La variante deve
    # essere richiesta esplicitamente, cosi' non puo' sovrascrivere per errore
    # le immagini destinate alla tesi.
    thesis = not args.variant
    if thesis:
        values = load_thesis_metrics()
        folder = args.out or THESIS_OUT
        extensions = ("png",)
    else:
        # La verifica dei dati sperimentali viene caricata solo quando la
        # variante e' richiesta esplicitamente.
        import verify_rq2_tables as tables

        checked = tables.verify()
        values = {(scenario, mode): row for scenario, mode, row in checked}
        folder = args.out or tables.VARIANT / "grafici"
        extensions = ("png", "svg")

    # 2. Parametri grafici fissati per rendere riproducibili stile e dimensioni.
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "svg.fonttype": "none", "axes.labelcolor": "#374151",
                         "text.color": "#172A3A"})
    folder.mkdir(parents=True, exist_ok=True)
    scenarios = tuple(MODES) if args.all else (args.scenario,)
    for scenario in scenarios:
        if thesis:
            name = f"grafico_scenario_{int(scenario[2:])}"
        else:
            name = f"complete_{scenario.lower()}"
        if thesis:
            fig, ax = plt.subplots(figsize=(11, 6.5))
            draw_metrics_scenario(ax, scenario, values)
            decorate_metrics(fig)
        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            draw_variant_scenario(ax, scenario, values)
            decorate_variant(fig)
        save(fig, folder, name, extensions=extensions)
        if args.show:
            plt.show()
        plt.close(fig)


if __name__ == "__main__":
    main()
