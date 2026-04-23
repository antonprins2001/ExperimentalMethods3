
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

    for seq_data in trial_seqs:
        if seq_data["Generated"]:
            trial = ProductionTrial(tree=seq_data["Sequence"], probs=seq_data["Probabilities"])