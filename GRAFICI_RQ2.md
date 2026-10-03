# Riprodurre i grafici definitivi di RQ2

Lo script genera un grafico a barre raggruppate per ciascuno scenario di RQ2.
Ogni grafico confronta Recall@k, Exact Match dei fatti e Correct Abstention
Rate. I valori vengono ricalcolati dalle annotazioni definitive conservate in
`RACCOLTA_RISULTATI/SC02`–`SC05`: lo script non rigenera risposte e non modifica
i giudizi.

## Da terminale

```bash
cd /Users/giorgiolai/Desktop/progetto_tirocinio
.venv-grafici/bin/python scripts/plot_rq2_results.py --all
```

Il comando rigenera questi quattro file:

- `risultati_tesi/RQ2/grafico_scenario_2.png`
- `risultati_tesi/RQ2/grafico_scenario_3.png`
- `risultati_tesi/RQ2/grafico_scenario_4.png`
- `risultati_tesi/RQ2/grafico_scenario_5.png`

Per rigenerare un solo grafico usa, per esempio:

```bash
.venv-grafici/bin/python scripts/plot_rq2_results.py --scenario SC02
```

Puoi aggiungere `--show` se vuoi anche visualizzare il grafico in una finestra
interattiva. Senza questa opzione lo script salva soltanto i file, quindi può
essere eseguito anche in un ambiente senza interfaccia grafica.

## Da PyCharm

1. Imposta l'interprete su `/Users/giorgiolai/Desktop/progetto_tirocinio/.venv-grafici/bin/python`.
2. Apri `scripts/plot_rq2_results.py`.
3. Modifica `SCENARIO = "SC02"` scegliendo lo scenario desiderato.
4. Premi **Run** sullo script.

Il grafico viene salvato nella cartella definitiva. Per mostrarlo anche dentro
PyCharm, aggiungi `--show` ai parametri della configurazione Run e abilita
**Settings → Tools → Python Plots → Show plots in tool window**.

In alternativa, imposta `--scenario SC03` nel campo Parameters della
configurazione Run. Il parametro prevale sulla variabile `SCENARIO`.

## Come funziona

- `load_thesis_metrics()` legge le sette annotazioni definitive di ogni
  architettura e scenario.
- **Recall@k** è la copertura micro dei fatti: somma dei fatti obbligatori
  presenti nel contesto divisa per la somma dei fatti obbligatori. Il valore di
  `k` è determinato, per ciascuna domanda, dagli elementi che entrano nel budget
  di 200 token.
- **Exact Match dei fatti** è il numero di risposte complete e supportate sulle
  sei domande per le quali l'oracle richiede una risposta.
- **Correct Abstention Rate** è il numero di astensioni corrette sulla domanda
  per la quale l'oracle richiede l'astensione.
- `plt.subplots()` crea figura e assi.
- `ax.bar()` disegna le colonne e `ax.text()` scrive le frazioni.
- `fig.savefig()` salva i PNG con dimensioni, carattere, colori e risoluzione
  fissati nel codice.

Le frazioni sono sempre riportate sopra le barre, così i denominatori piccoli
restano visibili. La cronologia completa è rossa perché è un controllo
diagnostico fuori budget. Per questa modalità Recall@k è indicato come `n.a.`:
la cronologia completa non esegue retrieval. Le altre architetture mantengono
lo stesso colore in tutti gli scenari.

## Variante sperimentale successiva

La prova successiva sul budget resta separata dai risultati definitivi. Per
riprodurne un grafico è necessario richiederla esplicitamente:

```bash
.venv-grafici/bin/python scripts/plot_rq2_results.py --variant --scenario SC02
```

In questo caso lo script usa `verify_rq2_tables.py` e salva PNG e SVG in
`results/rq2/budget_per_scenario_v1/grafici/`. L'opzione `--variant` evita che
questa prova venga confusa con i grafici destinati alla tesi.

## Installazione su un altro computer

```bash
python3 -m venv .venv-grafici
.venv-grafici/bin/python -m pip install -r requirements-grafici.txt
```
