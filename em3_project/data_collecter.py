
def CollectTrials(trial_seqs):

    test_data = {
        "Trial": [],
        "Generated": [],
        "Changed": [],
        "Guess": [],
        "Surprise_Cons": [],
        "Old_Tone": [],
        "Old_Tone_Surprise": [],
        "New_Tone": [],
        "New_Tone_Surprise": [],
        "Playback_Time_Start": [],
        "Playback_Time_Stop": [],
        "RT": []
    }

    trial_data = {
        "Trial": [],
        "Generated": [],
        "Changed": [],
        "Position": [],
        "Tone": [],
        "Surprise": [],
        "Alternative": [],
        "Alt_Surprise": [],
        "RT": []
    }

    for trial_num, seq_data in enumerate(trial_seqs):
        if seq_data["Generated"]:
            trial = ProductionTrial(tree=seq_data["Sequence"], probs=seq_data["Probabilities"])
            path_tones, path_probs, alt_tones, alt_probs, RTs, color = trial

            for i in range(len(path_tones)):
                trial_data["Trial"].append(trial_num)
                trial_data["Generated"].append(True)
                trial_data["Changed"].append(seq_data["Change"])
                trial_data["Position"].append(i+1)
                trial_data["Tone"].append(path_tones[i])
                trial_data["Surprise"].append(path_probs[i])
                trial_data["Alternative"].append(alt_tones[i])
                trial_data["Alt_Surprise"].append(alt_probs[i])
                trial_data["RT"].append(RTs[i])

            seq = path_tones

        else: #Memorization task
            trial = MemoryTrial(seq=seq_data["Sequence"])
            RTs, color = trial

            for i in range(len(seq_data["Sequence"])):
                trial_data["Trial"].append(trial_num)
                trial_data["Generated"].append(False)
                trial_data["Changed"].append(seq_data["Change"])
                trial_data["Position"].append(i+1)
                trial_data["Tone"].append(seq_data["Sequence"][i])
                trial_data["Surprise"].append(seq_data["Probabilities"][i])
                trial_data["Alternative"].append(None)
                trial_data["Alt_Surprise"].append(None)
                trial_data["RT"].append(RTs[i])
        
            seq = seq_data["Sequence"]

        if not seq_data["Change"]:
            test = TestTrial(seq, color)
            guess, rt = test

        
        else: #Alternative sequence
            new_seq = GenerateNewSeq(seq, seq_data["Position"], seq_data["Alternatives"], seq_data["Generated"], altpos)
            test = TestTrial(new_seq, color)
            guess, rt = test