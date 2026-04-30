def PracticeTrials(practice_seqs):

    for practice_num, seq_data in enumerate(practice_seqs):

        if seq_data["Generated"]:
            intro_text = "Practice trial\n\nThis is a production trial.\n\nPress any key to start."

            intro = visual.TextStim(
                win,
                text=intro_text,
                color=text_color,
                height=28
            )
            intro.draw()
            win.flip()
            event.waitKeys()

            trial = ProductionTrial(
                tree=seq_data["Sequence"],
                prob_tree=seq_data["Probabilites"],
                entropy_tree=seq_data["Entropy"],
                altposition=seq_data["Position"]
            )

            path_tones, path_probs, path_entropy, alt_tones, alt_probs, RTs, color, altpos = trial

            seq = path_tones
            probs = path_probs
            ents = path_entropy

        else:
            intro_text = "Practice trial\n\nThis is a memory trial.\n\nPress any key to start."

            intro = visual.TextStim(
                win,
                text=intro_text,
                color=text_color,
                height=28
            )
            intro.draw()
            win.flip()
            event.waitKeys()

            trial = MemoryTrial(
                tree=seq_data["Sequence"],
                prob_tree=seq_data["Probabilites"],
                entropy_tree=seq_data["Entropy"],
                altposition=seq_data["Position"]
            )

            path_tones, path_probs, path_entropy, alt_tones, alt_probs, RTs, color, altpos = trial

            seq = path_tones
            probs = path_probs
            ents = path_entropy

        if not seq_data["Change"]:
            guess, rt = TestTrial(
                seq,
                False,
                -1,
                color,
                seq_data["Generated"],
                seq_data["Surprisal"]
            )

        else:
            if seq_data["Generated"]:
                new_seq, alt_prob = GenerateNewSeq(
                    seq.copy(),
                    seq_data["Position"],
                    seq_data["Alternatives"],
                    altpos
                )
            else:
                new_seq, alt_prob = GenerateNewSeq(
                    seq.copy(),
                    seq_data["Position"],
                    [seq_data["Alternatives"]],
                    0
                )

            guess, rt = TestTrial(
                new_seq,
                True,
                seq_data["Position"],
                color,
                seq_data["Generated"],
                seq_data["Surprisal"]
            )

        outro = visual.TextStim(
            win,
            text="Practice trial finished.\n\nPress any key to continue.",
            color=text_color,
            height=28
        )
        outro.draw()
        win.flip()
        event.waitKeys()

    end_text = visual.TextStim(
        win,
        text="Practice is finished.\n\nPress any key to begin the real experiment.",
        color=text_color,
        height=28
    )
    end_text.draw()
    win.flip()
    event.waitKeys()