def PracticeTrials(trial_seqs):

    memory_practice = None
    production_practice = None

    for seq_data in trial_seqs:
        if seq_data["Generated"] == False and memory_practice is None:
            memory_practice = seq_data

        if seq_data["Generated"] == True and production_practice is None:
            production_practice = seq_data

        if memory_practice is not None and production_practice is not None:
            break

    # memory practice

    intro = visual.TextStim(
        win,
        text="Practice trial 1\n\nThis is a memory trial.\n\nPress any key to start.",
        color=text_color,
        height=28
    )
    intro.draw()
    win.flip()
    event.waitKeys()

    RTs, color = MemoryTrial(memory_practice["Sequence"])

    seq = memory_practice["Sequence"].copy()

    if not memory_practice["Change"]:
        guess, rt = TestTrial(seq, False, -1, color)

    else:

        new_seq, alt_prob = GenerateNewSeq(
            seq.copy(),
            memory_practice["Position"],
            [memory_practice["Alternatives"]],
            0
        )

        guess, rt = TestTrial(
            new_seq,
            True,
            memory_practice["Position"],
            color
        )

    outro = visual.TextStim(
        win,
        text="Memory practice is finished.\n\nPress any key to continue.",
        color=text_color,
        height=28
    )
    outro.draw()
    win.flip()
    event.waitKeys()

    # Production practice

    intro = visual.TextStim(
        win,
        text="Practice trial 2\n\nThis is a production trial.\n\nPress any key to start.",
        color=text_color,
        height=28
    )
    intro.draw()
    win.flip()
    event.waitKeys()

    trial = ProductionTrial(
        tree=production_practice["Sequence"],
        prob_tree=production_practice["Probabilites"],
        entropy_tree=production_practice["Entropy"],
        altposition=production_practice["Position"]
    )

    path_tones, path_probs, path_entropy, alt_tones, alt_probs, RTs, color, altpos = trial

    seq = path_tones.copy()

    if not production_practice["Change"]:
        guess, rt = TestTrial(seq, False, -1, color)

    else:
        new_seq, alt_prob = GenerateNewSeq(
            seq.copy(),
            production_practice["Position"],
            production_practice["Alternatives"],
            altpos
        )

        guess, rt = TestTrial(
            new_seq,
            True,
            production_practice["Position"],
            color
        )

    outro = visual.TextStim(
        win,
        text="Practice is finished.\n\nPress any key to begin the real experiment.",
        color=text_color,
        height=28
    )
    outro.draw()
    win.flip()
    event.waitKeys()

def CollectTrials(trial_seqs, subject_id):