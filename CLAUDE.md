# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Hvad er dette projekt?

Et kognitivt eksperiment der undersøger forholdet mellem **aktiv melodikomposition**, **information content (IC/surprisal)** og **hukommelse**. Projektet kombinerer et adfærdsparadigme, EEG og computational modellering. Udviklet til EM3 (Experimental Methods 3) på Københavns Universitet.

Projektet er under aktiv udvikling — forvent placeholders og work-in-progress strukturer.

## Forskningsspørgsmål

1. **Generationseffekten**: Husker man en melodi bedre, hvis man selv har komponeret den, fremfor blot at have lyttet til den?
2. **IC og hukommelse**: Påvirker en tones surprisal (information content) arousal og efterfølgende melodigenkaldelse?

## Eksperimentelt design

```
[Intro/Instruktion] → [Encoding-fase] → [Test-fase] → [Afslutning]
```

**Encoding-fase** — to betingelser per melodi (8 toner, diatonisk skala, konstant rytme):

- **Memoriseret**: Kumulativ præsentation [T1] → [T1,T2] → … → [T1..T8], gentaget ×2
- **Genereret**: Sekventielt 2AFC-valg, deltager vælger T1→T2→…→T8; IC af valgmuligheder styres af n-gram modellen, gentaget ×2

**Test-fase (Change Detection)**: Fuld 8-tone probe → *"Hørt før / Ikke hørt før?"* (primært mål: accuracy + RT). 2AFC recognition bruges som sekundær validering.

| Faktor | Niveauer |
|---|---|
| Encoding-type | Genereret vs. Memoriseret |
| Probe-type | Samme vs. Ændret |
| Surprisal-betingelse | ns→s, s→s, s→ns, ns→ns |
| Gentagelser | ×2 |

**Åbne designspørgsmål (ikke afklaret):**
- Surprisal i genereret-betingelse: manipuleret faktor eller kontinuert kovariat?
- EEG-rolle: manipulation check, primært outcome, eller mekanistisk probe?
- Runde 2 af genereret-betingelse: afspilles melodien igen, eller genskabes den aktivt?

## Computational model

Forenklet IDyOM-alternativ baseret på **bigram transitionsmatrix**:

- **Træningskorpus**: Lakh MIDI Dataset (LMD-matched) filtreret med Million Song Dataset genre-metadata (vestlig pop)
- **Afvist**: POP909 (kinesisk pop — matcher ikke deltagernes musikalske baggrund). Den nuværende `sequences.ipynb` bruger stadig POP909 og skal erstattes.
- **MIDI-parsing**: `pretty_midi` til melodisporisiolering
- **Output**: JSON med sandsynlighedsfordeling over næste tone + tonal hierarki

Pipeline: MSD metadata-filtrering → LMD-matched MIDI-udtræk → melodisporisiolering → bigram-træning *(ikke færdig endnu)*

## EEG

Tre kandidat-roller (ikke endeligt afklaret):
1. **Manipulation check**: MMN/P600 ved høj vs. lav IC bekræfter at manipulationen virker
2. **Primært outcome**: Old/new-effekt (FN400, LPC) stærkere for genererede vs. memoriserede melodier
3. **Mekanistisk probe**: IC under encoding predikterer later recall (EEG som mediator)

IDyOM-afledt per-tone surprisal er den centrale computationelle variabel.

## Nøglelitteratur

- **Mathias, Palmer, Perrin & Tillmann (2015, 2016)** — produktionslæring og pitch change detection
- **Agres, Abdallah & Pearce (2018)** — IDyOM-afledt IC og genkendelseshukommelse for tonesekvenser
- **Filipic, Tillmann & Bigand (2010)** — 2AFC melodigenkendelse hos ikke-musikere
- **Peretz, Gaudreau & Bonnel (1998)** — 2AFC melodigenkendelse hos ikke-musikere
- *Halpern (1984) understøtter IKKE 2AFC melodihukommelse hos ikke-musikere — undgå denne reference.*

## Running the Experiment

```bash
source .venv/bin/activate
cd em3_project
python super_script copy.py   # Working version — use this
```

`main.py` + `experiment.py` er i øjeblikket brudt (se Known Issues). Virtual environment: `.venv/` (Python 3.12.3). Ingen `requirements.txt` — afhængigheder installeret direkte i `.venv/`: `psychopy`, `pandas`, `numpy`, `mido` (+ `pretty_midi` til fremtidig pipeline).

## Kodearkitektur

### PsychoPy Experiment (`em3_project/`)

- [super_script copy.py](em3_project/super_script copy.py) — **De-facto entry point** (387 linjer). Konsoliderer alt eksperimentflow i ét script: trial-funktioner, datacollection, gemmer `data/{subject_id}_trial_data.csv` og `data/{subject_id}_test_data.csv`. Fikser response-logic bugs fra `trial.py`. Brug dette.
- [main.py](em3_project/main.py) — Tiltænkt entry point; kalder `Experiment().run()` — **brudt** (ingen Experiment-klasse i experiment.py).
- [experiment.py](em3_project/experiment.py) — Knap 20 linjer top-level kode uden Experiment-klasse; kører dog partialt (loader sequences, opretter vindue, kører trials). Matcher ikke `main.py`s interface.
- [settings.py](em3_project/settings.py) — Config-funktioner: `getSettings()` (vindue 1200×800, bg=blue, duration=0.4s, keys=["z","m"]), `getSubjectInfo()`, `getSubjectCharacteristics()`, `checkIfEscape()`. Har dangling kode linje 36-37.
- [trial.py](em3_project/trial.py) — `ConvertFreq`, `MemoryTrial`, `ProductionTrial`, `TestTrial`. Har response-key logic bug (linje ~108). Afhænger af globale variabler (`win`, `duration`, `clock`).
- [condition_manager.py](em3_project/condition_manager.py) — `GenerateTrials(path)`: loader sequences.csv og shuffler. **Kritisk bug linje 8**: `df.loc[0]` skal være `df.loc[i]` — genererer samme trial N gange.
- [data_collecter.py](em3_project/data_collecter.py) — `CollectTrials(trial_seqs)`: orkestrerer trial-flow, kalder Memory/ProductionTrial + TestTrial, returnerer to DataFrames.
- [participant.py](em3_project/participant.py) — Minimal datamodel (id + gruppe).
- [block.py](em3_project/block.py) — Tom stub.

### Stimulus-generering (`em3_project/Sequence/`)

- [sequences.ipynb](em3_project/Sequence/sequences.ipynb) — Bygger Markov-model og binære træer til sekventiel stimuluspræsentation. Bruger i øjeblikket POP909-datasættet — skal migreres til LMD+MSD.
- [Sequence/POP909-Dataset/](em3_project/Sequence/POP909-Dataset/) — Midlertidigt MIDI-korpus (skal erstattes)

## Tekniske konventioner

- Sprog i kode: **engelsk**
- Sprog i kommentarer og docs: **dansk eller engelsk** (konsistens pr. fil)
- MIDI-parsing: `pretty_midi`
- Model-output: JSON
- Eksperimentel interface: HTML/JS mockup i [design_mockup.html](em3_project/design_mockup.html); endelig platform ikke fastlagt

## Data-skemaer

**Input til eksperiment:** `Sequence/sequences.csv` (genereret af `sequences.ipynb`)

| Kolonne | Type | Beskrivelse |
|---------|------|-------------|
| `Generated` | bool | True = 2AFC-betingelse |
| `Change` | bool | True = probe har ændret tone |
| `Position` | int | Hvilken tone (0-7) er ændret |
| `Surprisal` | str (bool-tuple) | IC-betingelse: `(True,False)` = ns→s osv. |
| `Probe` | int | MIDI-notenummer for probe-tonen |
| `Sequence` | list[int] | 8 MIDI-noter |
| `Probabilites` | list[float] | Surprisal-værdier per tone |
| `Alternatives` | list[tuple] | `(tone, prob)` alternativ ved change-position |

**Output per deltager** (gemt i `data/`):
- `{id}_trial_data.csv`: `Trial, Generated, Changed, Position, Tone, Surprise, Alternative, Alt_Surprise, RT`
- `{id}_test_data.csv`: `Trial, Generated, Changed, Guess, Surprise_Cond, Old_Tone, Old_Tone_Surprise, New_Tone, New_Tone_Surprise, RT`

## Known Issues (aktive bugs)

| Fil | Linje | Problem |
|-----|-------|---------|
| `condition_manager.py` | 8 | `df.loc[0]` skal være `df.loc[i]` — alle trials er identiske |
| `trial.py` | ~108 | `not "z" in keys or "m" in keys` er altid True — response-logic er brudt (fikset i `super_script copy.py`) |
| `experiment.py` | — | Ingen `Experiment`-klasse; matcher ikke `main.py` |
| `settings.py` | 36-37 | DataFrame-save uden kontekst — krasjer ved import |

## Vigtige advarsler

- **Rytmeconfound**: Fri rytme i melodikomposition kan dominere hukommelsesenkodning over tonehøjde og underminere IC-manipulationen. Rytme skal holdes konstant.
- **Medieret vs. direkte model**: IC→hukommelse-hypotesen har to arkitektonisk forskellige former. At skelne dem kræver arousal-måling (fx SAM-skala).
- **Dataset**: MSD alene er utilstrækkeligt til symbolsk modellering (kun audio-features). Brug LMD-matched + MSD genre-filtrering.
