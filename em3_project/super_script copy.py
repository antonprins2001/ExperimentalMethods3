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

    tones = {}
    for note in sequence:
        freq = ConvertFreq(note)
        if freq not in tones:
            tones[note] = sound.Sound(value=freq, secs=duration, stereo=True, hamming=True)

    RTs = []

    square = visual.Rect(win,fillColor=col,size=[200, 200])
    square.draw()
    win.flip()

    for i in range(1, 9, 1):

        for j in range(i):
            tones[sequence[j]].play()
            core.wait(duration)

        core.wait(0.5)

        for j in range(i):
            tones[sequence[j]].play()
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
    altpos = -1
    RTs = []

    tones = {}
    for note in tree:
        if note not in tones:
            freq = ConvertFreq(note)
            tones[note] = sound.Sound(value=freq, secs=duration, stereo=True, hamming=True)

    trial_colors = ["red", "blue", "cyan", "yellow", "pink", "green", "purple"]
    col = random.choice(trial_colors)

    # Mockup color tokens
    C_PAGE    = [0.867, 0.851, 0.812]
    C_CARD    = 'white';   C_BD_CARD = '#dddddd'
    C_BG_SEC  = '#f5f4f0'; C_TX_SEC  = '#5f5e5a'; C_BD_SEC  = '#dedcda'
    C_BG_SUCC = '#eaf3de'; C_TX_SUCC = '#3b6d11'; C_BD_SUCC = '#b6d48e'
    C_BG_WARN = '#faeeda'; C_TX_WARN = '#854f0b'; C_BD_WARN = '#e0a96a'
    C_BG_A    = '#e6f1fb'; C_TX_A    = '#185fa5'; C_BD_A    = '#85b7eb'
    C_BG_B    = '#faeeda'; C_TX_B    = '#854f0b'; C_BD_B    = '#e0a96a'
    C_TX_PRI  = '#1a1a18'

    orig_bg = list(win.color)
    win.color = C_PAGE

    card      = visual.Rect(win, width=700, height=580, pos=(0, 0),
                            fillColor=C_CARD, lineColor=C_BD_CARD, lineWidth=1)
    badge_bg  = visual.Rect(win, width=236, height=26, pos=(0, 255),
                            fillColor=C_BG_SUCC, lineColor=C_BD_SUCC, lineWidth=1)
    badge_lbl = visual.TextStim(win, text='Encoding — genereret',
                                pos=(0, 255), color=C_TX_SUCC, height=12)
    subtitle    = visual.TextStim(win,
                    text='Vælg tonerne én ad gangen. Melodien opbygges og afspilles løbende.',
                    pos=(0, 210), color=C_TX_SEC, height=13)
    counter_txt = visual.TextStim(win, text='', pos=(0, 175), color=C_TX_SEC, height=12)

    # Option headline pill — prominent A/B label above tiles
    opt_pill_bg  = visual.Rect(win, width=260, height=36, pos=(0, 130),
                               fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
    opt_pill_lbl = visual.TextStim(win, text='', pos=(0, 130),
                                   color=C_TX_SEC, height=15)

    # 8 sequence tiles (46×46, spacing 60 px)
    TILE_STEP = 60
    tile_xs = [-(7 * TILE_STEP) / 2 + i * TILE_STEP for i in range(8)]
    tiles = [visual.Rect(win, width=46, height=46, pos=(x, 70),
                         fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
             for x in tile_xs]
    tile_nums = [visual.TextStim(win, text=str(i + 1), pos=(tile_xs[i], 70),
                                 color=C_TX_SEC, height=13)
                 for i in range(8)]

    hint_txt = visual.TextStim(win, text='Melodien opbygges og gentages 2× i alt',
                               pos=(0, 5), color=C_TX_SEC, height=12)

    # Color-coded choice buttons: A = blue, B = amber
    btn_l_bg  = visual.Rect(win, width=200, height=50, pos=(-115, -115),
                             fillColor=C_BG_A, lineColor=C_BD_A, lineWidth=1)
    btn_r_bg  = visual.Rect(win, width=200, height=50, pos=( 115, -115),
                             fillColor=C_BG_B, lineColor=C_BD_B, lineWidth=1)
    btn_l_txt = visual.TextStim(win, text='Tone A  [Z]', pos=(-115, -115),
                                color=C_TX_A, height=15)
    btn_r_txt = visual.TextStim(win, text='Tone B  [M]', pos=( 115, -115),
                                color=C_TX_B, height=15)

    color_cue = visual.Rect(win, fillColor=col, size=[36, 36], pos=(0, -255))

    def draw_scene(n_green, active_idx, opt_header, opt_color, show_buttons, counter=''):
        card.draw()
        badge_bg.draw(); badge_lbl.draw()
        subtitle.draw()
        counter_txt.text = counter; counter_txt.draw()

        # Option headline pill
        if opt_header:
            if opt_color == 'A':
                opt_pill_bg.fillColor = C_BG_A; opt_pill_bg.lineColor = C_BD_A
                opt_pill_lbl.color = C_TX_A
            elif opt_color == 'B':
                opt_pill_bg.fillColor = C_BG_B; opt_pill_bg.lineColor = C_BD_B
                opt_pill_lbl.color = C_TX_B
            else:
                opt_pill_bg.fillColor = C_BG_SEC; opt_pill_bg.lineColor = C_BD_SEC
                opt_pill_lbl.color = C_TX_SEC
            opt_pill_lbl.text = opt_header
            opt_pill_bg.draw(); opt_pill_lbl.draw()

        # 8 tiles — only active_idx lights up; confirmed tiles stay green
        for k, (t, lbl) in enumerate(zip(tiles, tile_nums)):
            if k == active_idx:
                if opt_color == 'A':
                    t.fillColor = C_BG_A; t.lineColor = C_BD_A; lbl.color = C_TX_A
                elif opt_color == 'B':
                    t.fillColor = C_BG_B; t.lineColor = C_BD_B; lbl.color = C_TX_B
                else:
                    t.fillColor = C_BG_WARN; t.lineColor = C_BD_WARN; lbl.color = C_TX_WARN
            elif k < n_green:
                t.fillColor = C_BG_SUCC; t.lineColor = C_BD_SUCC; lbl.color = C_TX_SUCC
            else:
                t.fillColor = C_BG_SEC; t.lineColor = C_BD_SEC; lbl.color = C_TX_SEC
            t.draw(); lbl.draw()

        hint_txt.draw()
        if show_buttons:
            btn_l_bg.draw(); btn_l_txt.draw()
            btn_r_bg.draw(); btn_r_txt.draw()
        color_cue.draw()
        win.flip()

    def play_option(path, n_confirmed, opt_label, opt_color, counter):
        # Confirmed tones play without tile animation (tiles stay green)
        for j in range(n_confirmed):
            draw_scene(n_green=n_confirmed, active_idx=-1,
                       opt_header=opt_label, opt_color=opt_color,
                       show_buttons=False, counter=counter)
            tones[path[j]].play()
            core.wait(duration)
        # New tone — only new tile lights up in option's color
        draw_scene(n_green=n_confirmed, active_idx=n_confirmed,
                   opt_header=opt_label, opt_color=opt_color,
                   show_buttons=False, counter=counter)
        tones[path[n_confirmed]].play()
        core.wait(duration)
        # New tile returns to pending after playback
        draw_scene(n_green=n_confirmed, active_idx=-1,
                   opt_header='', opt_color=None,
                   show_buttons=False, counter=counter)

    def play_animated(path, n_confirmed, counter=''):
        for j, note in enumerate(path):
            draw_scene(n_green=j, active_idx=j, opt_header='', opt_color=None,
                       show_buttons=False, counter=counter)
            tones[note].play()
            core.wait(duration)
        draw_scene(n_confirmed, active_idx=-1, opt_header='', opt_color=None,
                   show_buttons=False, counter=counter)

    play_animated(path_tones, n_confirmed=1, counter='Vælg tone 2 af 8')
    RTs.append(0.0)

    parent = 0

    for i in range(7):
        child1 = 2 * (parent + 1) - 1
        child2 = 2 * (parent + 1)
        altpos = -1
        n_confirmed = len(path_tones)
        counter = f'Vælg tone {n_confirmed + 1} af 8'

        play_option(path_tones + [tree[child1]], n_confirmed,
                    '▶ Option A', 'A', counter)
        core.wait(0.4)
        play_option(path_tones + [tree[child2]], n_confirmed,
                    '▶ Option B', 'B', counter)

        draw_scene(n_confirmed, active_idx=-1, opt_header='',
                   opt_color=None, show_buttons=True, counter=counter)
        clock.reset()

        response = False
        while not response:
            checkIfEscape()
            keys = event.getKeys(keyList=['z', 'm'])
            if 'z' in keys:
                choice = child1; alt = child2; response = True
            if 'm' in keys:
                choice = child2; alt = child1; response = True

        RTs.append(clock.getTime())

        if i == altposition:
            altpos = parent - 2**i + 1

        parent = choice
        path_tones.append(tree[choice])
        path_probs.append(prob_tree[choice])
        alt_tones.append(tree[alt])
        alt_probs.append(prob_tree[alt])

    for rep in range(2):
        play_animated(path_tones, n_confirmed=8,
                      counter=f'Melodien afspilles ({rep + 1}/2)...')
        if rep == 0:
            core.wait(0.3)

    draw_scene(8, active_idx=-1, opt_header='', opt_color=None,
               show_buttons=False, counter='Alle 8 toner valgt')
    win.color = orig_bg
    return path_tones, path_probs, alt_tones, alt_probs, RTs, col, altpos

def TestTrial(seq, change, pos, col):
    # Mockup color tokens
    C_PAGE    = [0.867, 0.851, 0.812]
    C_CARD    = 'white';   C_BD_CARD = '#dddddd'
    C_BG_SEC  = '#f5f4f0'; C_TX_SEC  = '#5f5e5a'; C_BD_SEC  = '#dedcda'
    C_BG_A    = '#e6f1fb'; C_TX_A    = '#185fa5'; C_BD_A    = '#85b7eb'
    C_BG_DGR  = '#fcebeb'; C_TX_DGR  = '#a32d2d'; C_BD_DGR  = '#f09595'
    C_TX_PRI  = '#1a1a18'

    tones = {}
    for note in seq:
        if note not in tones:
            freq = ConvertFreq(note)
            tones[note] = sound.Sound(value=freq, secs=duration, stereo=True, hamming=True)

    orig_bg = list(win.color)
    win.color = C_PAGE

    card      = visual.Rect(win, width=700, height=580, pos=(0, 0),
                            fillColor=C_CARD, lineColor=C_BD_CARD, lineWidth=1)
    badge_bg  = visual.Rect(win, width=76, height=26, pos=(0, 255),
                            fillColor=C_BG_DGR, lineColor=C_BD_DGR, lineWidth=1)
    badge_lbl = visual.TextStim(win, text='Test', pos=(0, 255),
                                color=C_TX_DGR, height=12)
    heading   = visual.TextStim(win, text='Er dette den samme melodi som du hørte?',
                                pos=(0, 195), color=C_TX_PRI, height=17)
    subhead   = visual.TextStim(win, text='', pos=(0, 150), color=C_TX_SEC, height=13)

    TILE_STEP = 60
    tile_xs = [-(7 * TILE_STEP) / 2 + i * TILE_STEP for i in range(8)]
    tiles = [visual.Rect(win, width=46, height=46, pos=(x, 70),
                         fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
             for x in tile_xs]
    tile_nums = [visual.TextStim(win, text=str(i + 1), pos=(tile_xs[i], 70),
                                 color=C_TX_SEC, height=13)
                 for i in range(8)]

    status_txt  = visual.TextStim(win, text='', pos=(0, 10), color=C_TX_SEC, height=13)
    btn_yes_bg  = visual.Rect(win, width=210, height=50, pos=(-120, -85),
                               fillColor=C_CARD, lineColor='#aaaaaa', lineWidth=1)
    btn_no_bg   = visual.Rect(win, width=210, height=50, pos=( 120, -85),
                               fillColor=C_CARD, lineColor='#aaaaaa', lineWidth=1)
    btn_yes_txt = visual.TextStim(win, text='Ja, samme  (M)', pos=(-120, -85),
                                  color=C_TX_PRI, height=15)
    btn_no_txt  = visual.TextStim(win, text='Nej, forskellig  (Z)', pos=( 120, -85),
                                  color=C_TX_PRI, height=15)
    col_cue = visual.Rect(win, fillColor=col, size=[36, 36], pos=(0, -220))

    def draw_test(active_idx, status, show_buttons, subheading=''):
        card.draw()
        badge_bg.draw(); badge_lbl.draw()
        heading.draw()
        subhead.text = subheading; subhead.draw()
        for k, (t, lbl) in enumerate(zip(tiles, tile_nums)):
            if k == active_idx:
                t.fillColor = C_BG_A; t.lineColor = C_BD_A; lbl.color = C_TX_A
            else:
                t.fillColor = C_BG_SEC; t.lineColor = C_BD_SEC; lbl.color = C_TX_SEC
            t.draw(); lbl.draw()
        status_txt.text = status; status_txt.draw()
        if show_buttons:
            btn_yes_bg.draw(); btn_yes_txt.draw()
            btn_no_bg.draw(); btn_no_txt.draw()
        col_cue.draw()
        win.flip()

    draw_test(active_idx=-1, status='', show_buttons=False,
              subheading='Tryk en tast for at lytte')
    event.waitKeys()

    for i, note in enumerate(seq):
        if i == pos - 1 and change:
            print("Noget med en form for eeg trigger her")
        else:
            print("Noget med en anden form for eeg trigger her")
        draw_test(active_idx=i, status='▶ Afspiller...', show_buttons=False,
                  subheading='Lyt opmærksomt')
        tones[note].play()
        core.wait(duration)

    draw_test(active_idx=-1, status='', show_buttons=True,
              subheading='Var det den samme melodi?')
    clock.reset()

    response = False
    while not response:
        checkIfEscape()
        keys = event.getKeys(keyList=['z', 'm'])
        if 'z' in keys:
            guess = True; response = True
        if 'm' in keys:
            guess = False; response = True

    rt = clock.getTime()
    win.color = orig_bg
    return guess, rt


def GenerateNewSeq(seq, pos, alts, altpos):
    
    new_seq = seq
    alt_tone, alt_prob = alts[altpos]
    new_seq[pos-1] = alt_tone

    return new_seq, alt_prob

def CollectTrials(trial_seqs, subject_id):

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

            os.makedirs("data", exist_ok=True)
            trial_file = f"data/{subject_id}_trial_data.csv"
            test_file = f"data/{subject_id}_test_data.csv"

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

        pd.DataFrame(trial_data).to_csv(trial_file, index=False)
        pd.DataFrame(test_data).to_csv(test_file, index=False)

    return test_data, trial_data

path = "Sequence/sequences.csv"
trial_seqs = GenerateTrials(path)

fullscreen, window_size, bg_color, text_color, duration, response_keys = getSettings()
win = visual.Window(size=window_size, color = bg_color, units = "pix")
clock = core.Clock()

subject_id = getSubjectInfo()
test_data, trial_data = CollectTrials(trial_seqs, subject_id)

core.quit()

