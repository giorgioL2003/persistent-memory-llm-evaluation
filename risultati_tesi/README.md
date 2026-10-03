# Risultati numerici organizzati per domanda di ricerca

La raccolta contiene una sola tabella CSV per ogni domanda di ricerca:

- `RQ1/tabella_risultati.csv`
- `RQ2/tabella_risultati.csv`
- `RQ3/tabella_risultati.csv`
- `RQ4/tabella_risultati.csv`
- `RQ5/tabella_risultati.csv`

Ogni tabella contiene i risultati numerici principali da usare nel capitolo
della tesi. Le celle `NA` indicano una metrica non applicabile, non un valore
pari a zero.

Fonti originali: `results/metrics_pilot.json`,
`RACCOLTA_RISULTATI/sintesi_rq2.csv` e i file `summary.csv` delle valutazioni
RQ3, RQ4 e RQ5 presenti sotto `results/`.

## Grafici di RQ2

I quattro grafici definitivi di RQ2 mostrano Recall@k, Exact Match dei fatti e
Correct Abstention Rate. Sono ricalcolati direttamente dalle annotazioni
definitive in `RACCOLTA_RISULTATI/SC02`–`SC05`. Dalla cartella principale del
progetto si rigenerano tutti con:

```bash
.venv-grafici/bin/python scripts/plot_rq2_results.py --all
```

Il procedimento completo e la distinzione dalla successiva variante
sperimentale sono descritti in `GRAFICI_RQ2.md`.
