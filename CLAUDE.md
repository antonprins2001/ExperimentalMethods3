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

IDyOM-afledt per-tone surprisal er den centrale computationelle variabel.

### ERP-komponenter og deres rolle

| Komponent | Latens | Distribution | Fase | Rolle |
|-----------|--------|--------------|------|-------|
| **N1** | ~100 ms | Fronto-central | Encoding (per tone-onset) | Tidlig auditiv opmærksomhed og akustisk overraskelse — forventes større amplitude ved høj IC |
| **P200** | ~200 ms | Fronto-central | Encoding (per tone-onset) | Automatisk processering af tonale forventninger — forventes moduleret af IC |
| **P300** | ~300–500 ms | Centro-parietal (P3b) / Frontal (P3a) | Encoding + test-fase | Under encoding: kontekstopdatering ved høj-IC toner. Under test: change-detection markør — forventes forstærket for Genereret-betingelse |
| **FN400** | ~300–500 ms | Fronto-central | Test-fase | Familiarity-baseret old/new-effekt — uændret probe → mere positiv FN400. Hypotese: stærkere for Genereret > Memoriseret |

### Mapping til hypoteser

**H1 – Generationseffekten:**
- FN400 (test-fase): Stærkere old/new-forskel for Genereret > Memoriseret
- P300 (test-fase): Større change-detection respons for Genereret > Memoriseret

**H2 – IC og enkodning:**
- N1 + P200 (encoding, per-tone): Amplitude korrelerer med per-tone IC
- P300 (encoding): Forstærket kontekstopdatering ved uventede (høj-IC) toner

### Trigger-implementering (i `main_difficult.py`)

Port: `serial.Serial("/dev/tty.usbserial-DN2Q03LO", 115200)` via `setup_eeg_trigger()` — falder automatisk tilbage til mock-print hvis porten ikke er tilgængelig. Practice-trials bruger `send_triggers=False` og forurener ikke optagelsen.

**Encoding-triggers** — `EncodingTriggerCode(generated, position)` → 2-cifret kode `[condition][position]`:
- Condition: `1` = Memorized, `2` = Generated
- Position: tone-nummer 0–4 (5-tone melodi)
- Sendes via `win.callOnFlip()` i `play_animated()` — kun ved afsluttende replay, ikke under A/B-præsentation

**Test-triggers** — `TestTriggerCode(generated, surprisal, position)` → 3-cifret kode `[condition][surprisal_cond][position]`:
- Surprisal-condition: `0` = ikke-changed tone, `1`=(T,T), `2`=(F,F), `3`=(F,T), `4`=(T,F)
- Sendes per tone-onset under probe-afspilning via `win.callOnFlip()`
- `80`: decision-onset (response-knapper vises) via `win.callOnFlip()`
- `90`: response-timestamp — sendes direkte (ikke via callOnFlip) umiddelbart efter tastetryk

| Trigger-type | Kode | Eksempel | Tidspunkt |
|---|---|---|---|
| Tone-onset encoding (Memorized) | `1[0-4]` | `10`–`14` | `play_animated()` replay |
| Tone-onset encoding (Generated) | `2[0-4]` | `20`–`24` | `play_animated()` replay |
| Tone-onset test — ikke-changed | `[1/2]0[0-4]` | `100`–`104` | Per tone i probe |
| Tone-onset test — changed tone | `[1/2][1-4][0-4]` | `214` | Kun ved ændret position |
| Decision-onset | `80` | `80` | Når respons-knapper vises |
| Response | `90` | `90` | Umiddelbart efter tastetryk |

**Kendte mangler:**
- **Ingen IC i encoding-koden**: `EncodingTriggerCode` indkoder kun condition + position — IC-niveau kan ikke epocheres direkte uden merge med CSV i post-processing.
- **Option-toner triggeres ikke**: `play_option()` under valg-fasen sender ingen triggers — N1/P200 til beslutningstonerne kan ikke analyseres.
- **Ingen trial-onset marker**: Ingen trigger markerer starten af en ny trial.

### Fravalgte komponenter

- **MMN**: Kræver passiv oddball-paradigme — passer ikke til aktivt 2AFC-design
- **P600**: Primært syntaktisk reanalyse i sprog — svag teoretisk begrundelse her
- **LPC**: Potentielt relevant (recollection), men nedprioriteret da familiarity (FN400) er den primære mekanisme i change-detection

## Nøglelitteratur

- **Mathias, Palmer, Perrin & Tillmann (2015, 2016)** — produktionslæring og pitch change detection
- **Agres, Abdallah & Pearce (2018)** — IDyOM-afledt IC og genkendelseshukommelse for tonesekvenser
- **Filipic, Tillmann & Bigand (2010)** — 2AFC melodigenkendelse hos ikke-musikere
- **Peretz, Gaudreau & Bonnel (1998)** — 2AFC melodigenkendelse hos ikke-musikere
- *Halpern (1984) understøtter IKKE 2AFC melodihukommelse hos ikke-musikere — undgå denne reference.*

## Running the Experiment

```bash
source .venv/bin/activate
python main_difficult.py   # Primær eksperimentfil med EEG-triggers
```

Virtual environment: `.venv/` (Python 3.12.3). Ingen `requirements.txt` — afhængigheder installeret direkte i `.venv/`: `psychopy`, `pandas`, `numpy`, `mido` (+ `pretty_midi` til fremtidig pipeline).

## Kodearkitektur

### PsychoPy Experiment (rod-mappen)

`main_difficult.py` er **de-facto entry point** — selvstændig monolitisk fil med alle funktioner og fuldt EEG-trigger-setup.

- [main_difficult_with_triggers.py](main_difficult_with_triggers.py) — **Brug dette.** 5-tone melodier, 4 binære valg. Indeholder: `setup_eeg_trigger()`, `EncodingTriggerCode()`, `TestTriggerCode()`, `build_visuals()`, `MemoryTrial()`, `ProductionTrial()`, `TestTrial()`, `PracticeTrials()`, `GenerateNewSeq()`, `CollectTrials()`. Læser `Sequence/sequences_dif.csv`. Gemmer `data/{subject_id}_trial_data.csv` + `data/{subject_id}_test_data.csv` løbende.
- [main_difficult.py](main_difficult.py) — Samme som ovenstående uden EEG-triggers (reference/backup).
- [em3_project/super_script copy.py](em3_project/super_script copy.py) — Ældre 8-tone version. Beholdt som reference.
- [em3_project/super_script.py](em3_project/super_script.py) — Endnu ældre version. Har `df.loc[0]`-buggen — brug ikke.
- Øvrige filer i `em3_project/` (`main.py`, `experiment.py`, `trial.py`, osv.) — dead code fra ældre arkitektur. Ignorér dem.

**Nøglefunktioner i main_difficult_with_triggers.py:**

- `setup_eeg_trigger(port, baud)` — returnerer `(trigger_fn, port_obj)`; falder back til mock hvis porten fejler
- `MemoryTrial(tree, ..., send_triggers=True)` — computeren vælger random A/B, deltager trykker `[space]`
- `ProductionTrial(tree, ..., send_triggers=True)` — deltager vælger `[z]`=A / `[m]`=B
- `TestTrial(seq, change, pos, col, generated, surprisal, send_triggers=True)` — probe-afspilning + change-detection respons
- `CollectTrials(trial_seqs, subject_id)` — trial-par-logik (even=encoding, odd=encoding+test×2)

**Binært træ-struktur**: `Sequence` er en liste af MIDI-noder. Rod = `[0]`. For forælder `p`: venstre barn = `2*(p+1)-1`, højre barn = `2*(p+1)`. Loop kører `range(2, 6)` → 4 valg → 5-tone path.

### Stimulus-generering (`em3_project/Sequence/`)

- [sequences.ipynb](em3_project/Sequence/sequences.ipynb) — Bygger Markov-model og binære træer. Bruger stadig POP909-datasættet — skal migreres til LMD+MSD.
- [sequences_surprisal.ipynb](em3_project/Sequence/sequences_surprisal.ipynb) — Nyere notebook til surprisal-beregning og CSV-generering.
- `sequences_new.csv` — Produktions-CSV (bruges af main.py).
- `sequences_test.csv` — Forkortet CSV til hurtig test/simulate (bruges af main_backup.py).
- `practice_sequences.csv` — Practice trials (PracticeTrials er pt. kommenteret ud i main.py).
- [Sequence/POP909-Dataset/](em3_project/Sequence/POP909-Dataset/) — Midlertidigt MIDI-korpus (skal erstattes)

## Tekniske konventioner

- Sprog i kode: **engelsk**
- Sprog i kommentarer og docs: **dansk eller engelsk** (konsistens pr. fil)
- MIDI-parsing: `pretty_midi`
- Model-output: JSON
- Eksperimentel interface: HTML/JS mockup i [design_mockup.html](em3_project/design_mockup.html); endelig platform ikke fastlagt

## Data-skemaer

**Input til eksperiment:** `Sequence/sequences_new.csv` (genereret af notebooks)

| Kolonne | Type | Beskrivelse |
|---------|------|-------------|
| `Generated` | bool | True = 2AFC-betingelse |
| `Change` | bool | True = probe har ændret tone |
| `Position` | int | Hvilken tone (1-8) er ændret |
| `Surprisal` | str (bool-tuple) | IC-betingelse: `(True,False)` = ns→s osv. |
| `Sequence` | list[int] | 15 MIDI-noder (binært træ, indeks 0–14) |
| `Probabilites` | list[float] | Surprisal-værdier per node |
| `Entropy` | list[float] | Entropi per node |
| `PitchDif` | list[float] | Pitch difference per node (ny kolonne) |
| `Alternatives` | list[tuple] | `(tone, prob)` alternativ ved change-position |

**Output per deltager** (gemt i `data/`, skrives inkrementelt efter hvert trial):
- `{id}_trial_data.csv`: `Trial, Generated, Changed, Position, Tone, Surprise, Alternative, Alt_Surprise, PitchDif, Entropy, RT`
- `{id}_test_data.csv`: `Trial, Generated, Changed, Guess, Surprise_Cond, Position, Old_Tone, Old_Tone_Surprise, New_Tone, New_Tone_Surprise, PitchDif, Entropy, RT`

## Known Issues (aktive bugs)

Bugs i de gamle moduler (trial.py, condition_manager.py, super_script.py, experiment.py) er **ikke relevante** — brug kun main.py.

| Fil | Problem |
|-----|---------|
| `main.py` — `MemoryTrial` | Loop kører `range(7)` (7 iterationer) men `range(2,9,1)` i ProductionTrial (7 iterationer). Begge giver 8 toner inkl. rod-tonen — men loop-indeks bruges til altposition-beregning, så formlen kan afvige mellem de to. Verificér. |
| `main.py` — `altpos`-beregning | Formlen `(parent - 2**i + 1) // 4` i MemoryTrial/ProductionTrial er uverificeret — det er uklart om den korrekt mapper tree-indeks til `Alternatives`-list-indeks. |
| `main.py` — EEG triggers | `trigger()`-kald er kommenteret ud (`#trigger(code, port)`). Port-variablen er også kommenteret ud. EEG-integration skal genaktiveres manuelt. |
| `main.py` — `PracticeTrials` | Kaldet er kommenteret ud i top-level kode. |
| `super_script.py` | `df.loc[0]`-bug (linje 54) — alle trials identiske. Brug ikke. |

## Vigtige advarsler

- **Rytmeconfound**: Fri rytme i melodikomposition kan dominere hukommelsesenkodning over tonehøjde og underminere IC-manipulationen. Rytme skal holdes konstant.
- **Medieret vs. direkte model**: IC→hukommelse-hypotesen har to arkitektonisk forskellige former. At skelne dem kræver arousal-måling (fx SAM-skala).
- **Dataset**: MSD alene er utilstrækkeligt til symbolsk modellering (kun audio-features). Brug LMD-matched + MSD genre-filtrering.
