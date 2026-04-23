

def ConvertFreq(tone):
    return round(440 * (2**((tone - 69)/12)), 3)

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

def ProductionTrial(tree, prob_tree):
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

    for i in range(7):

        child1 = 2*(parent+1)-1
        child2 = 2*(parent+1)

        path1 = path_tones + tree[child1]
        path2 = path_tones + tree[child2]

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
        
        while not "z" in keys or "m" in keys:
            keys = event.getKeys(keyList = ["z", "m"])
            if "z" in keys:
                choice = child1
                alt = child2
            if "m" in keys:
                choice = child2
                alt = child1
        
        RTs.append(clock.getTime())

        path_tones.append(tree[choice])
        path_probs.append(prob_tree[choice])

        alt_tones.append(tree[alt])
        alt_probs.append(prob_tree[alt])

    return path_tones, path_probs, alt_tones, alt_probs, RTs, col

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
    
    while not "z" in keys or "m" in keys:
        keys = event.getKeys(keyList = ["z", "m"])
        if "z" in keys:
            guess = True
        if "m" in keys:
            guess = False
    
    rt = clock.getTime()

    return guess, rt
