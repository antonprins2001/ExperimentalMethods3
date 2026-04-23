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
