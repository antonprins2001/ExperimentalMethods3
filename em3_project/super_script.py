from psychopy import visual, core, event, sound, gui
import pandas as pd
import ast
import numpy as np
import os

from settings import getSettings
from participant import Participant
from trial import ConvertFreq, MemoryTrial, ProductionTrial, TestTrial
from data_collecter import CollectTrials
from condition_manager import GenerateTrials


def getSettings():
    fullscreen = False
    window_size = (1200, 800)
    bg_color = "blue"
    text_color = "white"

    duration = 0.4

    response_keys = ["z", "m"]

    return fullscreen, window_size, bg_color, text_color, duration, response_keys

def getSubjectInfo():
    info = {'FID': 0}
    dlg = gui.DlgFromDict(dictionary=info, title='n-Armed Bandit Experiment')
    if not dlg.OK:
        core.quit()
    return info['FID']

def getSubjectCharacteristics():
    info = {'Age': 0, 'Gender (F/M/Other)': ' '}
    dlg = gui.DlgFromDict(dictionary=info, title='n-Armed Bandit Experiment')
    if not dlg.OK:
        core.quit()
    return info['Age'], info['Gender (F/M/Other)']

def checkIfEscape():
    keys = event.getKeys()
    if 'escape' in keys:
        core.quit()

def GenerateTrials(path):
    df_order = pd.read_csv(path)
    df = df_order.sample(frac=1)

    for col in ["Sequence", "Probabilites", "Surprisal", "Alternatives"]:
        df[col] = df[col].apply(ast.literal_eval)

    trial_data = []
    for i in range(len(df.index)):
        trial = df.loc[0].to_dict()
        trial["trial"] = i
        trial_data.append(trial)
    return trial_data

import random

def ConvertFreq(tone):
    return round(440 * (2**((int(tone) - 69)/12)), 3)

def MemoryTrial(sequence):
    colors = ["red", "blue", "cyan", "yellow", "pink", "green", "purple"]
    col = random.choice(colors)

    RTs = []

    square = visual.Rect(win,fillColor=col,size=[200, 200])
    square.draw()
    win.flip()

    for i in range(1, 9, 1):
        print("Playing " + str(i) + " tones")

        for j in range(i):
            freq = ConvertFreq(sequence[j])
            tone = sound.Sound(value=freq, secs=duration)
            tone.play()
            core.wait(duration)

        core.wait(0.5)

        for j in range(i):
            freq = ConvertFreq(sequence[j])
            tone = sound.Sound(value=freq, secs=duration)
            tone.play()
            core.wait(duration)

        clock.reset()
        event.waitKeys() #Måske noget andet
        RTs.append(clock.getTime())

    testMessage = visual.TextStim(win, text="Playing the full melody, Press key", pos= [0, -150], color="black")
    square.draw()
    testMessage.draw()
    win.flip()
    event.waitKeys()

    for i, tone in enumerate(sequence):
        freq = ConvertFreq(sequence[i])
        tone = sound.Sound(value=freq, secs=duration)
        tone.play()
        core.wait(duration)
    win.flip()

    return RTs, col

def ProductionTrial(tree, prob_tree, altposition):
    path_tones = [tree[0]]
    path_probs = [prob_tree[0]]
    alt_tones = [None]
    alt_probs = [None]

    RTs = []

    parent = 0

    colors = ["red", "blue", "cyan", "yellow", "pink", "green", "purple"]
    col = random.choice(colors)

    square = visual.Rect(win,fillColor=col,size=[200, 200])
    firstMSG = visual.TextStim(win, text="First version", pos= [0, -150], color="black")
    secondMSG = visual.TextStim(win, text="Second version", pos= [0, -150], color="black")

    square.draw()
    win.flip()

    freq = ConvertFreq(path_tones[0])
    tone = sound.Sound(value=freq, secs=duration)
    tone.play()
    clock.reset()
    event.waitKeys()
    RTs.append(clock.getTime())


    for i in range(7):

        child1 = 2*(parent+1)-1
        child2 = 2*(parent+1)

        path1 = path_tones + [tree[child1]]
        path2 = path_tones + [tree[child2]]

        altpos = -1

        square.draw()
        firstMSG.draw()
        win.flip()

        for tone in path1:
            freq = ConvertFreq(tone)
            tone = sound.Sound(value=freq, secs=duration)
            tone.play()
            core.wait(duration)
        
        square.draw()
        secondMSG.draw()
        win.flip()

        core.wait(0.5)

        for tone in path2:
            freq = ConvertFreq(tone)
            tone = sound.Sound(value=freq, secs=duration)
            tone.play()
            core.wait(duration)

        testMessage = visual.TextStim(win, text="Press M for the first version and Z for the second version", pos= [0, -150], color="black")
        square.draw()
        testMessage.draw()
        win.flip()
        clock.reset()
        
        response = False
        while not response:
            keys = event.getKeys(keyList = ["z", "m"])
            if "z" in keys:
                choice = child1
                alt = child2
                response = True
            if "m" in keys:
                choice = child2
                alt = child1
                response = True
        
        RTs.append(clock.getTime())

        if i == altposition:
            altpos = parent-2**i+1

        parent = choice
    
        path_tones.append(tree[choice])
        path_probs.append(prob_tree[choice])

        alt_tones.append(tree[alt])
        alt_probs.append(prob_tree[alt])

    return path_tones, path_probs, alt_tones, alt_probs, RTs, col, altpos

def TestTrial(seq, change, pos, col):
    testMessage = visual.TextStim(win, text="Is the following melody the same as before? Press key", pos= [0, 0], color="black")
    testMessage.draw()
    win.flip()
    event.waitKeys()

    square = visual.Rect(win,fillColor=col,size=[200, 200])
    square.draw()
    win.flip()

    for i, tone in enumerate(seq):
        freq = ConvertFreq(seq[i])
        tone = sound.Sound(value=freq, secs=duration)
        if i == pos - 1 and change:
            print("Noget med en form for eeg trigger her")
        else:
            print("Noget med en anden form for eeg trigger her")
        tone.play()
        core.wait(duration)
    
    testMessage = visual.TextStim(win, text="Was it the same melody as before?, Press M for yes and Z for no", pos= [0, -150], color="black")
    square.draw()
    testMessage.draw()
    win.flip()
    clock.reset()
    
    response = False
    while not response:
        keys = event.getKeys(keyList = ["z", "m"])
        if "z" in keys:
            guess = True
            response = True
        if "m" in keys:
            guess = False
            response = True
    
    rt = clock.getTime()

    return guess, rt


def GenerateNewSeq(seq, pos, alts, altpos):
    
    new_seq = seq
    alt_tone, alt_prob = alts[altpos]
    new_seq[pos-1] = alt_tone

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
                print("i=",i)
                print("len(RTs)=",len(RTs))
                print("RTs=",RTs)
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
                print("i=",i)
                print("len(RTs)=",len(RTs))
                print("RTs=",RTs)
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

path = "Sequence/sequences.csv"
trial_seqs = GenerateTrials(path)

fullscreen, window_size, bg_color, text_color, duration, response_keys = getSettings()
win = visual.Window(size=window_size, color = bg_color, units = "pix")
clock = core.Clock()

test_data, trial_data = CollectTrials(trial_seqs)

core.quit()

