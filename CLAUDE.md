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
python main.py
```

Virtual environment: `.venv/` (Python 3.12.3). Ingen `requirements.txt` — afhængigheder er installeret direkte i `.venv/`.

## Kodearkitektur

### PsychoPy Experiment (`em3_project/`)

- [main.py](em3_project/main.py) — Entry point; initialiserer PsychoPy-vindue og starter eksperimentet
- [experiment.py](em3_project/experiment.py) — Hoved-flowkontroller; importerer `DataManager` fra `data_manager.py` som **ikke eksisterer endnu** (giver ImportError ved kørsel)
- [settings.py](em3_project/settings.py) — Central config: vindue (1200×800), timing (`STIMULUS_TIME=1.0s`, `BREAK_TIME=0.5s`), responstastar (`left`/`right`), `N_BLOCKS=2`
- [participant.py](em3_project/participant.py) — Deltager-datamodel (id + betingelse)

**Stub-filer (tomme, ikke implementeret endnu):**
[block.py](em3_project/block.py), [trial.py](em3_project/trial.py), [condition_manager.py](em3_project/condition_manager.py), [data_collecter.py](em3_project/data_collecter.py)

### Stimulus-generering (`em3_project/Sequence/`)

- [sequences.ipynb](em3_project/Sequence/sequences.ipynb) — Bygger Markov-model og binære træer til sekventiel stimuluspræsentation. Bruger i øjeblikket POP909-datasættet — skal migreres til LMD+MSD.
- [Sequence/POP909-Dataset/](em3_project/Sequence/POP909-Dataset/) — Midlertidigt MIDI-korpus (skal erstattes)

## Tekniske konventioner

- Sprog i kode: **engelsk**
- Sprog i kommentarer og docs: **dansk eller engelsk** (konsistens pr. fil)
- MIDI-parsing: `pretty_midi`
- Model-output: JSON
- Eksperimentel interface: HTML/JS mockup i [design_mockup.html](em3_project/design_mockup.html); endelig platform ikke fastlagt

## Vigtige advarsler

- **Rytmeconfound**: Fri rytme i melodikomposition kan dominere hukommelsesenkodning over tonehøjde og underminere IC-manipulationen. Rytme skal holdes konstant.
- **Medieret vs. direkte model**: IC→hukommelse-hypotesen har to arkitektonisk forskellige former. At skelne dem kræver arousal-måling (fx SAM-skala).
- **Dataset**: MSD alene er utilstrækkeligt til symbolsk modellering (kun audio-features). Brug LMD-matched + MSD genre-filtrering.
