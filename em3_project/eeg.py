import serial

port = serial.Serial("COM4", 115200)  # address for serial port is COM4 in this example. Change to match your machine.

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

print(TestTriggerCode(True, (False, True), 7))

def trigger(code, port):
    port.write(code.to_bytes(1, 'big'))
    print('trigger sent {}'.format(code))



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
            if 'space' in keys:
                if random.choice([True,False]):
                    choice = child1; alt = child2; response = True
                else:
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