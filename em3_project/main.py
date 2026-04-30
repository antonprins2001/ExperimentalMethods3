from psychopy import visual, core, event, sound, gui
import pandas as pd
import ast
import numpy as np
import os
import serial
from git.em3_project.Backups.participant import Participant

def getSettings():
    fullscreen = False
    window_size = (1200, 800)
    bg_color = [0.867, 0.851, 0.812]
    text_color = "black"

    duration = 0.4

    response_keys = ["z", "m"]

    return fullscreen, window_size, bg_color, text_color, duration, response_keys

def getSubjectInfo():
    info = {'FID': 0}
    dlg = gui.DlgFromDict(dictionary=info, title='Music and Memory Experiment')
    if not dlg.OK:
        core.quit()
    return info['FID']

def getSubjectCharacteristics():
    info = {'Age': 0, 'Gender (F/M/Other)': ' '}
    dlg = gui.DlgFromDict(dictionary=info, title='Music and Memory Experiment')
    if not dlg.OK:
        core.quit()
    return info['Age'], info['Gender (F/M/Other)']

def checkIfEscape():
    keys = event.getKeys()
    if 'escape' in keys:
        core.quit()

def TestTriggerCode(generated, surprisal, position):
    if generated:
        cond = "2"
    else:
        cond = "1"
    if not surprisal:
        surp = "0"
    else:
        if surprisal == (True, True):
            surp = "1"
        elif surprisal == (False, False):
            surp = "2"
        elif surprisal == (False, True):
            surp = "3"
        elif surprisal == (True, False):
            surp = "4"
    pos = str(position)

    code = cond + surp + pos
    return(int(code))

def trigger(code, port):
    port.write(code.to_bytes(1, 'big'))
    print('trigger sent {}'.format(code))

def GenerateTrials(path):
    df_order = pd.read_csv(path)
    df = df_order.sample(frac=1).reset_index(drop=True)
    

    for col in ["Sequence", "Probabilites", "Surprisal", "Alternatives", "Entropy"]:
        df[col] = df[col].apply(safe_literal_eval)

    trial_data = []
    for i in range(len(df.index)):
        trial = df.iloc[i].to_dict()
        trial["trial"] = i
        trial_data.append(trial)
    return trial_data

def GeneratePracticeTrials(path):
    df = pd.read_csv(path)
    
    for col in ["Sequence", "Probabilites", "Surprisal", "Alternatives", "Entropy"]:
        df[col] = df[col].apply(safe_literal_eval)

    trial_data = []
    for i in range(len(df.index)):
        trial = df.iloc[i].to_dict()
        trial["trial"] = i
        trial_data.append(trial)
    return trial_data

import random

def introMessage():
    C_PAGE    = [0.867, 0.851, 0.812]
    C_CARD    = 'white';   C_BD_CARD = '#dddddd'
    C_BG_SEC  = '#f5f4f0'; C_BD_SEC  = '#dedcda'
    C_BG_SUCC = '#eaf3de'; C_BD_SUCC = '#b6d48e'
    C_BG_WARN = '#faeeda'; C_BD_WARN = '#e0a96a'
    C_BG_A    = '#e6f1fb'; C_TX_A    = '#185fa5'; C_BD_A    = '#85b7eb'
    C_BG_B    = '#faeeda'; C_TX_B    = '#854f0b'; C_BD_B    = '#e0a96a'
    C_TX_PRI  = '#1a1a18'

    orig_bg = list(win.color)
    win.color = C_PAGE

    card = visual.Rect(win, width=700, height=580, pos=(0, 0),
                       fillColor=C_CARD, lineColor=C_BD_CARD, lineWidth=1)
    intro = visual.TextStim(win, text= "Welcome to the experiment! You will in the following hour be doing both memorization of a small 8-tones melodies, " \
    "aswell as producing your own melody through 8 binary choices between two tones. You job is to remember the melodies, and afterwards determine whether it has been changed or not." \
    " We start off with som practice trials. Press any key to start.", pos= [0, 0], color=text_color)
    card.draw()
    intro.draw()
    win.flip()
    event.waitKeys()

def ConvertFreq(tone):
    return round(440 * (2**((int(tone) - 69)/12)), 3)

def safe_literal_eval(x):
    if isinstance(x, str):
        return ast.literal_eval(x)
    else:
        return x

def MemoryTrial(tree, prob_tree, entropy_tree, altposition):
    path_tones = [tree[0]]
    path_probs = [prob_tree[0]]
    path_entropy = [entropy_tree[0]]
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

    C_PAGE    = [0.867, 0.851, 0.812]
    C_CARD    = 'white';   C_BD_CARD = '#dddddd'
    C_BG_SEC  = '#f5f4f0'; C_BD_SEC  = '#dedcda'
    C_BG_SUCC = '#eaf3de'; C_BD_SUCC = '#b6d48e'
    C_BG_WARN = '#faeeda'; C_BD_WARN = '#e0a96a'
    C_BG_A    = '#e6f1fb'; C_TX_A    = '#185fa5'; C_BD_A    = '#85b7eb'
    C_BG_B    = '#faeeda'; C_TX_B    = '#854f0b'; C_BD_B    = '#e0a96a'
    C_TX_PRI  = '#1a1a18'

    orig_bg = list(win.color)
    win.color = C_PAGE

    card = visual.Rect(win, width=700, height=580, pos=(0, 0),
                       fillColor=C_CARD, lineColor=C_BD_CARD, lineWidth=1)

    # Option headline pill — A/B label above tiles
    opt_pill_bg  = visual.Rect(win, width=260, height=36, pos=(0, 130),
                               fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
    opt_pill_lbl = visual.TextStim(win, text='', pos=(0, 130),
                                   color=C_BG_SEC, height=15)

    # 8 sequence tiles (46×46, spacing 60 px)
    TILE_STEP = 60
    tile_xs = [-(7 * TILE_STEP) / 2 + i * TILE_STEP for i in range(8)]
    tiles = [visual.Rect(win, width=46, height=46, pos=(x, 70),
                         fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
             for x in tile_xs]

    # Orange hollow border shown around whichever tile is playing
    orange_border = visual.Rect(win, width=54, height=54, pos=(0, 70),
                                fillColor=None, lineColor='orange', lineWidth=3)

    space_btn_bg  = visual.Rect(win, width=200, height=50, pos=(0, -115),
                                fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
    space_btn_txt = visual.TextStim(win, text='Press space to continue', pos=(0, -115),
                                    color=C_TX_PRI, height=15)

    color_cue = visual.Rect(win, fillColor=col, size=[36, 36], pos=(0, -255))

    def draw_scene(n_green, active_idx, opt_header, opt_color, show_buttons):
        card.draw()

        if opt_header:
            if opt_color == 'A':
                opt_pill_bg.fillColor = C_BG_A; opt_pill_bg.lineColor = C_BD_A
                opt_pill_lbl.color = C_TX_A
            elif opt_color == 'B':
                opt_pill_bg.fillColor = C_BG_B; opt_pill_bg.lineColor = C_BD_B
                opt_pill_lbl.color = C_TX_B
            else:
                opt_pill_bg.fillColor = C_BG_SEC; opt_pill_bg.lineColor = C_BD_SEC
                opt_pill_lbl.color = C_BG_SEC
            opt_pill_lbl.text = opt_header
            opt_pill_bg.draw(); opt_pill_lbl.draw()

        for k, t in enumerate(tiles):
            if k == active_idx and k == n_green:
                # New tile: option color (blue for A, amber for B)
                if opt_color == 'A':
                    t.fillColor = C_BG_A; t.lineColor = C_BD_A
                elif opt_color == 'B':
                    t.fillColor = C_BG_B; t.lineColor = C_BD_B
                else:
                    t.fillColor = C_BG_WARN; t.lineColor = C_BD_WARN
            elif k < n_green:
                # Confirmed tiles: always green (orange border added below if active)
                t.fillColor = C_BG_SUCC; t.lineColor = C_BD_SUCC
            else:
                t.fillColor = C_BG_SEC; t.lineColor = C_BD_SEC
            t.draw()

        # Orange hollow border around the currently playing tile
        if active_idx >= 0:
            orange_border.pos = (tile_xs[active_idx], 70)
            orange_border.draw()

        if show_buttons:
            space_btn_bg.draw(); space_btn_txt.draw()
        color_cue.draw()
        win.flip()

    def play_option(path, n_confirmed, opt_label, opt_color):
        for j in range(n_confirmed):
            draw_scene(n_green=n_confirmed, active_idx=j,
                       opt_header=opt_label, opt_color=opt_color,
                       show_buttons=False)
            tones[path[j]].play()
            core.wait(duration)
        draw_scene(n_green=n_confirmed, active_idx=n_confirmed,
                   opt_header=opt_label, opt_color=opt_color,
                   show_buttons=False)
        tones[path[n_confirmed]].play()
        core.wait(duration)
        # No trailing draw — buttons appear immediately after option B finishes

    def play_root_tone(note):
        draw_scene(n_green=1, active_idx=0, opt_header='', opt_color=None, show_buttons=False)
        tones[note].play()
        core.wait(duration)
        core.wait(1.0)
        draw_scene(1, active_idx=-1, opt_header='', opt_color=None, show_buttons=False)

    def play_animated(path, n_confirmed):
        for j, note in enumerate(path):
            draw_scene(n_green=n_confirmed, active_idx=j, opt_header='', opt_color=None,
                       show_buttons=False)
            tones[note].play()
            core.wait(duration)
        draw_scene(n_confirmed, active_idx=-1, opt_header='', opt_color=None,
                   show_buttons=False)

    def draw_intro():
        card.draw()
        prompt_txt = visual.TextStim(win, text='Remember the melody being composed by the computer',
                                 pos=(0, 0), color=C_TX_PRI, height=27)
        prompt_txt.draw()
        win.flip()

    def draw_choice(choice, n_green, active_idx):
        card.draw()
        if choice == 'A':
            opt_pill_bg.fillColor = C_BG_A; opt_pill_bg.lineColor = C_BD_A
            opt_pill_lbl.color = C_TX_A
        elif choice == 'B':
            opt_pill_bg.fillColor = C_BG_B; opt_pill_bg.lineColor = C_BD_B
            opt_pill_lbl.color = C_TX_B
        else:
            opt_pill_bg.fillColor = C_BG_SEC; opt_pill_bg.lineColor = C_BD_SEC
            opt_pill_lbl.color = C_BG_SEC
        opt_pill_lbl.text = "The computer chose " + choice
        opt_pill_bg.draw(); opt_pill_lbl.draw()

        for k, t in enumerate(tiles):
            if k == active_idx and k == n_green:
                # New tile: option color (blue for A, amber for B)
                if choice == 'A':
                    t.fillColor = C_BG_A; t.lineColor = C_BD_A
                elif choice == 'B':
                    t.fillColor = C_BG_B; t.lineColor = C_BD_B
                else:
                    t.fillColor = C_BG_WARN; t.lineColor = C_BD_WARN
            elif k < n_green:
                # Confirmed tiles: always green (orange border added below if active)
                t.fillColor = C_BG_SUCC; t.lineColor = C_BD_SUCC
            else:
                t.fillColor = C_BG_SEC; t.lineColor = C_BD_SEC
            t.draw()

        space_btn_bg.draw(); space_btn_txt.draw()
        color_cue.draw()
        win.flip()

    draw_intro()
    core.wait(2)

    play_root_tone(path_tones[0])
    RTs.append(0.0)

    parent = 0

    for i in range(7):
        child1 = 2 * (parent + 1) - 1
        child2 = 2 * (parent + 1)
        altpos = -1
        n_confirmed = len(path_tones)

        play_option(path_tones + [tree[child1]], n_confirmed, '▶ Option A', 'A')
        core.wait(0.4)
        play_option(path_tones + [tree[child2]], n_confirmed, '▶ Option B', 'B')
        
        if random.choice([True,False]):
            choice = child1; alt = child2
            draw_choice("A", n_confirmed, active_idx=-1)
        else:
            choice = child2; alt = child1
            draw_choice("B", n_confirmed, active_idx=-1)

        clock.reset()

        event.clearEvents()
        response = False
        while not response:
            keys = event.getKeys(keyList=['space', 'escape'])
            if 'escape' in keys:
                core.quit()
            if 'space' in keys:
                response = True

        RTs.append(clock.getTime())

        if i == altposition:
            altpos = parent - 2**i + 1

        parent = choice
        path_tones.append(tree[choice])
        path_probs.append(prob_tree[choice])
        path_entropy.append(entropy_tree[choice])
        alt_tones.append(tree[alt])
        alt_probs.append(prob_tree[alt])

        core.wait(0.5)

    play_animated(path_tones, n_confirmed=8)

    draw_scene(8, active_idx=-1, opt_header='', opt_color=None, show_buttons=False)
    win.color = orig_bg
    return path_tones, path_probs, path_entropy, alt_tones, alt_probs, RTs, col, altpos

def ProductionTrial(tree, prob_tree, entropy_tree, altposition):
    path_tones = [tree[0]]
    path_probs = [prob_tree[0]]
    path_entropy = [entropy_tree[0]]
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

    C_PAGE    = [0.867, 0.851, 0.812]
    C_CARD    = 'white';   C_BD_CARD = '#dddddd'
    C_BG_SEC  = '#f5f4f0'; C_BD_SEC  = '#dedcda'
    C_BG_SUCC = '#eaf3de'; C_BD_SUCC = '#b6d48e'
    C_BG_WARN = '#faeeda'; C_BD_WARN = '#e0a96a'
    C_BG_A    = '#e6f1fb'; C_TX_A    = '#185fa5'; C_BD_A    = '#85b7eb'
    C_BG_B    = '#faeeda'; C_TX_B    = '#854f0b'; C_BD_B    = '#e0a96a'
    C_TX_PRI  = '#1a1a18'

    orig_bg = list(win.color)
    win.color = C_PAGE

    card = visual.Rect(win, width=700, height=580, pos=(0, 0),
                       fillColor=C_CARD, lineColor=C_BD_CARD, lineWidth=1)

    # Option headline pill — A/B label above tiles
    opt_pill_bg  = visual.Rect(win, width=260, height=36, pos=(0, 130),
                               fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
    opt_pill_lbl = visual.TextStim(win, text='', pos=(0, 130),
                                   color=C_BG_SEC, height=15)

    # 8 sequence tiles (46×46, spacing 60 px)
    TILE_STEP = 60
    tile_xs = [-(7 * TILE_STEP) / 2 + i * TILE_STEP for i in range(8)]
    tiles = [visual.Rect(win, width=46, height=46, pos=(x, 70),
                         fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
             for x in tile_xs]

    # Orange hollow border shown around whichever tile is playing
    orange_border = visual.Rect(win, width=54, height=54, pos=(0, 70),
                                fillColor=None, lineColor='orange', lineWidth=3)

    # Choice buttons: A = blue (left/Z), B = amber (right/M)
    btn_l_bg  = visual.Rect(win, width=200, height=50, pos=(-115, -115),
                             fillColor=C_BG_A, lineColor=C_BD_A, lineWidth=1)
    btn_r_bg  = visual.Rect(win, width=200, height=50, pos=( 115, -115),
                             fillColor=C_BG_B, lineColor=C_BD_B, lineWidth=1)
    btn_l_txt = visual.TextStim(win, text='Tone A  [Z]', pos=(-115, -115),
                                color=C_TX_A, height=15)
    btn_r_txt = visual.TextStim(win, text='Tone B  [M]', pos=( 115, -115),
                                color=C_TX_B, height=15)

    color_cue = visual.Rect(win, fillColor=col, size=[36, 36], pos=(0, -255))

    def draw_scene(n_green, active_idx, opt_header, opt_color, show_buttons):
        card.draw()

        if opt_header:
            if opt_color == 'A':
                opt_pill_bg.fillColor = C_BG_A; opt_pill_bg.lineColor = C_BD_A
                opt_pill_lbl.color = C_TX_A
            elif opt_color == 'B':
                opt_pill_bg.fillColor = C_BG_B; opt_pill_bg.lineColor = C_BD_B
                opt_pill_lbl.color = C_TX_B
            else:
                opt_pill_bg.fillColor = C_BG_SEC; opt_pill_bg.lineColor = C_BD_SEC
                opt_pill_lbl.color = C_BG_SEC
            opt_pill_lbl.text = opt_header
            opt_pill_bg.draw(); opt_pill_lbl.draw()

        for k, t in enumerate(tiles):
            if k == active_idx and k == n_green:
                # New tile: option color (blue for A, amber for B)
                if opt_color == 'A':
                    t.fillColor = C_BG_A; t.lineColor = C_BD_A
                elif opt_color == 'B':
                    t.fillColor = C_BG_B; t.lineColor = C_BD_B
                else:
                    t.fillColor = C_BG_WARN; t.lineColor = C_BD_WARN
            elif k < n_green:
                # Confirmed tiles: always green (orange border added below if active)
                t.fillColor = C_BG_SUCC; t.lineColor = C_BD_SUCC
            else:
                t.fillColor = C_BG_SEC; t.lineColor = C_BD_SEC
            t.draw()

        # Orange hollow border around the currently playing tile
        if active_idx >= 0:
            orange_border.pos = (tile_xs[active_idx], 70)
            orange_border.draw()

        if show_buttons:
            btn_l_bg.draw(); btn_l_txt.draw()
            btn_r_bg.draw(); btn_r_txt.draw()
        color_cue.draw()
        win.flip()

    def play_option(path, n_confirmed, opt_label, opt_color):
        for j in range(n_confirmed):
            draw_scene(n_green=n_confirmed, active_idx=j,
                       opt_header=opt_label, opt_color=opt_color,
                       show_buttons=False)
            tones[path[j]].play()
            core.wait(duration)
        draw_scene(n_green=n_confirmed, active_idx=n_confirmed,
                   opt_header=opt_label, opt_color=opt_color,
                   show_buttons=False)
        tones[path[n_confirmed]].play()
        core.wait(duration)
        # No trailing draw — buttons appear immediately after option B finishes

    def play_root_tone(note):
        draw_scene(n_green=1, active_idx=0, opt_header='', opt_color=None, show_buttons=False)
        tones[note].play()
        core.wait(duration)
        core.wait(1.0)
        draw_scene(1, active_idx=-1, opt_header='', opt_color=None, show_buttons=False)

    def play_animated(path, n_confirmed):
        for j, note in enumerate(path):
            draw_scene(n_green=n_confirmed, active_idx=j, opt_header='', opt_color=None,
                       show_buttons=False)
            tones[note].play()
            core.wait(duration)
        draw_scene(n_confirmed, active_idx=-1, opt_header='', opt_color=None,
                   show_buttons=False)

    def draw_intro():
        card.draw()
        prompt_txt = visual.TextStim(win, text='Remember the melody being composed by your own choices',
                                 pos=(0, 0), color=C_TX_PRI, height=27)
        prompt_txt.draw()
        win.flip()

    draw_intro()
    core.wait(2)


    play_root_tone(path_tones[0])
    RTs.append(0.0)

    parent = 0

    for i in range(7):
        child1 = 2 * (parent + 1) - 1
        child2 = 2 * (parent + 1)
        altpos = -1
        n_confirmed = len(path_tones)

        play_option(path_tones + [tree[child1]], n_confirmed, '▶ Option A', 'A')
        core.wait(0.4)
        play_option(path_tones + [tree[child2]], n_confirmed, '▶ Option B', 'B')

        draw_scene(n_confirmed, active_idx=-1, opt_header='',
                   opt_color=None, show_buttons=True)
        clock.reset()

        event.clearEvents()
        response = False
        while not response:
            keys = event.getKeys(keyList=['z', 'm', 'escape'])
            if 'escape' in keys:
                core.quit()
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
        path_entropy.append(entropy_tree[choice])
        alt_tones.append(tree[alt])
        alt_probs.append(prob_tree[alt])

    play_animated(path_tones, n_confirmed=8)

    draw_scene(8, active_idx=-1, opt_header='', opt_color=None, show_buttons=False)
    win.color = orig_bg
    return path_tones, path_probs, path_entropy, alt_tones, alt_probs, RTs, col, altpos

def TestTrial(seq, change, pos, col, generated, surprisal):
    C_PAGE    = [0.867, 0.851, 0.812]
    C_CARD    = 'white';   C_BD_CARD = '#dddddd'
    C_BG_SEC  = '#f5f4f0'; C_BD_SEC  = '#dedcda'
    C_BG_SUCC = '#eaf3de'; C_BD_SUCC = '#b6d48e'
    C_TX_PRI  = '#1a1a18'

    tones = {}
    for note in seq:
        if note not in tones:
            freq = ConvertFreq(note)
            tones[note] = sound.Sound(value=freq, secs=duration, stereo=True, hamming=True)

    orig_bg = list(win.color)
    win.color = C_PAGE

    card = visual.Rect(win, width=700, height=580, pos=(0, 0),
                       fillColor=C_CARD, lineColor=C_BD_CARD, lineWidth=1)

    TILE_STEP = 60
    tile_xs = [-(7 * TILE_STEP) / 2 + i * TILE_STEP for i in range(8)]
    tiles = [visual.Rect(win, width=46, height=46, pos=(x, 70),
                         fillColor=C_BG_SEC, lineColor=C_BD_SEC, lineWidth=1)
             for x in tile_xs]

    # Orange hollow border shown around whichever tile is playing
    orange_border = visual.Rect(win, width=54, height=54, pos=(0, 70),
                                fillColor=None, lineColor='orange', lineWidth=3)

    # z = left = "Ja, samme", m = right = "Nej, forskellig"
    btn_yes_bg  = visual.Rect(win, width=210, height=50, pos=(-120, -85),
                               fillColor=C_CARD, lineColor='#aaaaaa', lineWidth=1)
    btn_no_bg   = visual.Rect(win, width=210, height=50, pos=( 120, -85),
                               fillColor=C_CARD, lineColor='#aaaaaa', lineWidth=1)
    btn_yes_txt = visual.TextStim(win, text='Ja, samme  [Z]', pos=(-120, -85),
                                  color=C_TX_PRI, height=15)
    btn_no_txt  = visual.TextStim(win, text='Nej, forskellig  [M]', pos=( 120, -85),
                                  color=C_TX_PRI, height=15)
    col_cue = visual.Rect(win, fillColor=col, size=[36, 36], pos=(0, -220))
    heading = visual.TextStim(win, text='Is this the same melody as you heard?',
                              pos=(0, 195), color=C_TX_PRI, height=17)
    prompt_txt = visual.TextStim(win, text='Press any key to listen to the melody',
                                 pos=(0, 155), color=C_TX_PRI, height=13)

    def draw_test(active_idx, show_buttons, show_prompt=False):
        card.draw()
        heading.draw()
        if show_prompt:
            prompt_txt.draw()
        for k, t in enumerate(tiles):
            if k == active_idx:
                t.fillColor = C_BG_SUCC; t.lineColor = C_BD_SUCC
            else:
                t.fillColor = C_BG_SEC; t.lineColor = C_BD_SEC
            t.draw()
        if active_idx >= 0:
            orange_border.pos = (tile_xs[active_idx], 70)
            orange_border.draw()
        if show_buttons:
            btn_yes_bg.draw(); btn_yes_txt.draw()
            btn_no_bg.draw(); btn_no_txt.draw()
        col_cue.draw()
        win.flip()

    draw_test(active_idx=-1, show_buttons=False, show_prompt=True)
    event.waitKeys()

    for i, note in enumerate(seq):
        draw_test(active_idx=i, show_buttons=False)
        if i == pos - 1 and change:
            code = TestTriggerCode(generated, surprisal, i)
        else:
            code = TestTriggerCode(generated, False, i)
        #trigger(code, port)
        tones[note].play()
        core.wait(duration)

    draw_test(active_idx=-1, show_buttons=True)
    event.clearEvents()
    clock.reset()

    response = False
    while not response:
        keys = event.getKeys(keyList=['z', 'm', 'escape'])
        if 'escape' in keys:
            core.quit()
        if 'z' in keys:
            guess = False; response = True   # z = left = Ja, samme
        if 'm' in keys:
            guess = True; response = True  # m = right = Nej, forskellig

    rt = clock.getTime()
    win.color = orig_bg

    def draw_feedback(correct):
        card.draw()

        if correct:
            textstim = visual.TextStim(win, text='The answer was correct!',
                              pos=(0, 0), color="#25fb45", height=17)
        else:
            textstim = visual.TextStim(win, text='The answer was false!',
                              pos=(0, 0), color="#ff3838", height=17)

        textstim.draw()
        col_cue.draw()
        win.flip()
        core.wait(1)

    draw_feedback((guess==change))

    return guess, rt

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
        "Position": [],
        "Old_Tone": [],
        "Old_Tone_Surprise": [],
        "New_Tone": [],
        "New_Tone_Surprise": [],
        "Entropy": [],
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
        "Entropy": [],
        "RT": []
    }

    os.makedirs("data", exist_ok=True)
    trial_file = f"data/{subject_id}_trial_data.csv"
    test_file  = f"data/{subject_id}_test_data.csv"

    for trial_num, seq_data in enumerate(trial_seqs):

        if seq_data["Generated"]:
            trial = ProductionTrial(tree=seq_data["Sequence"], prob_tree=seq_data["Probabilites"],
                                    entropy_tree=seq_data["Entropy"], altposition=seq_data["Position"])
            path_tones, path_probs, path_entropy, alt_tones, alt_probs, RTs, color, altpos = trial

            for i in range(len(path_tones)):
                trial_data["Trial"].append(trial_num)
                trial_data["Generated"].append(True)
                trial_data["Changed"].append(seq_data["Change"])
                trial_data["Position"].append(i+1)
                trial_data["Tone"].append(path_tones[i])
                trial_data["Surprise"].append(path_probs[i])
                trial_data["Alternative"].append(alt_tones[i])
                trial_data["Alt_Surprise"].append(alt_probs[i])
                trial_data["Entropy"].append(path_entropy[i])
                trial_data["RT"].append(RTs[i])

            seq = path_tones
            probs = path_probs
            ents = path_entropy

        else: #Memorization task
            trial = MemoryTrial(tree=seq_data["Sequence"], prob_tree=seq_data["Probabilites"],
                                    entropy_tree=seq_data["Entropy"], altposition=seq_data["Position"])
            path_tones, path_probs, path_entropy, alt_tones, alt_probs, RTs, color, altpos = trial

            for i in range(len(path_tones)):
                trial_data["Trial"].append(trial_num)
                trial_data["Generated"].append(False)
                trial_data["Changed"].append(seq_data["Change"])
                trial_data["Position"].append(i+1)
                trial_data["Tone"].append(path_tones[i])
                trial_data["Surprise"].append(path_probs[i])
                trial_data["Alternative"].append(alt_tones[i])
                trial_data["Alt_Surprise"].append(alt_probs[i])
                trial_data["Entropy"].append(path_entropy[i])
                trial_data["RT"].append(RTs[i])

            seq = path_tones
            probs = path_probs
            ents = path_entropy

        if not seq_data["Change"]:
            test = TestTrial(seq, False, -1, color, seq_data["Generated"], seq_data["Surprisal"])
            guess, rt = test

            test_data["Trial"].append(trial_num)
            test_data["Generated"].append(seq_data["Generated"])
            test_data["Changed"].append(False)
            test_data["Guess"].append(guess)
            test_data["Surprise_Cond"].append(seq_data["Surprisal"])
            test_data["Position"].append(None)
            test_data["Old_Tone"].append(None)
            test_data["Old_Tone_Surprise"].append(None)
            test_data["New_Tone"].append(None)
            test_data["New_Tone_Surprise"].append(None)
            test_data["Entropy"].append(None)
            test_data["RT"].append(rt)


        else:
            if seq_data["Generated"]:
                new_seq, alt_prob = GenerateNewSeq(seq, seq_data["Position"], seq_data["Alternatives"], altpos)
            else:
                new_seq, alt_prob = GenerateNewSeq(seq, seq_data["Position"], [seq_data["Alternatives"]], 0)
            test = TestTrial(new_seq, True, seq_data["Position"], color, seq_data["Generated"], seq_data["Surprisal"])
            guess, rt = test

            test_data["Trial"].append(trial_num)
            test_data["Generated"].append(seq_data["Generated"])
            test_data["Changed"].append(True)
            test_data["Guess"].append(guess)
            test_data["Surprise_Cond"].append(seq_data["Surprisal"])
            test_data["Position"].append(seq_data["Position"])
            test_data["Old_Tone"].append(seq[seq_data["Position"]-1])
            test_data["Old_Tone_Surprise"].append(probs[seq_data["Position"]-1])
            test_data["New_Tone"].append(new_seq[seq_data["Position"]-1])
            test_data["New_Tone_Surprise"].append(alt_prob)
            test_data["Entropy"].append(ents[seq_data["Position"]-1])
            test_data["RT"].append(rt)

        pd.DataFrame(trial_data).to_csv(trial_file, index=False)
        pd.DataFrame(test_data).to_csv(test_file, index=False)

    return test_data, trial_data

path = "Sequence/sequences.csv"
practice_path = 'Sequence/practice_sequences.csv'

trial_seqs = GenerateTrials(path)
practice_seqs = GeneratePracticeTrials(practice_path)

fullscreen, window_size, bg_color, text_color, duration, response_keys = getSettings()
win = visual.Window(size=window_size, color = bg_color, units = "pix")
clock = core.Clock()
#port = serial.Serial('/dev/tty.usbserial-DN2Q03LO', 115200)  # address for serial port is COM4 in this example. Change to match your machine.

subject_id = getSubjectInfo()

introMessage()

PracticeTrials(practice_seqs)

test_data, trial_data = CollectTrials(trial_seqs, subject_id)

#port.close()

core.quit()

