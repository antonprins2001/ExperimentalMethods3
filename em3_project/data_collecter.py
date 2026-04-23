from trial import ProductionTrial, MemoryTrial, TestTrial


def GenerateNewSeq(seq, pos, alts, altpos):
    
    new_seq = seq
    new_seq[pos-1] = alts[altpos]
    return new_seq
    
    return new_seq, alt_prob

def CollectTrials(trial_seqs):

    test_data = {
        "Trial": [],
        "Generated": [],
        "Changed": [],
        "Guess": [],
        "Surprise_Cond": [],
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
            trial = ProductionTrial(tree=seq_data["Sequence"], prob_tree=seq_data["Probabilites"], altposition = seq_data["Position"])
            path_tones, path_probs, alt_tones, alt_probs, RTs, color, altpos = trial

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
            probs = path_probs

        else: #Memorization task
            trial = MemoryTrial(seq=seq_data["Sequence"])
            RTs, color = trial
            altpos = 0

            for i in range(len(seq_data["Sequence"])):
                trial_data["Trial"].append(trial_num)
                trial_data["Generated"].append(False)
                trial_data["Changed"].append(seq_data["Change"])
                trial_data["Position"].append(i+1)
                trial_data["Tone"].append(seq_data["Sequence"][i])
                trial_data["Surprise"].append(seq_data["Probabilites"][i])
                trial_data["Alternative"].append(None)
                trial_data["Alt_Surprise"].append(None)
                trial_data["RT"].append(RTs[i])
        
            seq = seq_data["Sequence"]
            probs = seq_data["Probabilites"]

        if not seq_data["Change"]:
            test = TestTrial(seq, False, -1, color)
            guess, rt = test

            test_data["Trial"].append(trial_num)
            test_data["Generated"].append(seq_data["Generated"])
            test_data["Changed"].append(False)
            test_data["Guess"].append(guess)
            test_data["Surprise_Cond"].append(seq_data["Surprisal"])
            test_data["Old_Tone"].append(None)
            test_data["Old_Tone_Surprise"].append(None)
            test_data["New_Tone"].append(None)
            test_data["New_Tone_Surprise"].append(None)
            test_data["RT"].append(rt)

        
        else: #Alternative sequence
            new_seq, alt_prob = GenerateNewSeq(seq, seq_data["Position"], seq_data["Alternatives"], altpos)
            test = TestTrial(new_seq, True, seq_data["Position"], color)
            guess, rt = test

            test_data["Trial"].append(trial_num)
            test_data["Generated"].append(seq_data["Generated"])
            test_data["Changed"].append(True)
            test_data["Guess"].append(guess)
            test_data["Surprise_Cond"].append(seq_data["Surprisal"])
            test_data["Old_Tone"].append(seq[seq_data["Position"]-1])
            test_data["Old_Tone_Surprise"].append(probs[seq_data["Position"]-1])
            test_data["New_Tone"].append(new_seq[seq_data["Position"]-1])
            test_data["New_Tone_Surprise"].append(alt_prob)
            test_data["RT"].append(rt)
        
    return test_data, trial_data