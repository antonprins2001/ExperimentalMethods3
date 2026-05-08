# A simple oddball experiment for EEG demo
#   cf Näätänen et al 1978 (https://doi.org/10.1016/0001-6918(78)90006-9)
from psychopy import visual, core, sound, event, parallel
import random
import serial

# Parameters
n_trials        = 1000  # Total number of trials
deviant_prob    = 0.2  # Probability of a deviant tone

# Create a window
win = visual.Window([800, 600])

################################################################################
# FUNCITONS
################################################################################

# MAKE TRIAL STRUCTURE
def make_triallist(length, ratio):
    num_ones = int(length*ratio)
    num_zeros = length-num_ones
    array = [1]*num_ones

    pos = 2  # Ensure the first 3 stimuli are standard
    for ii in range(num_zeros):
        pos = pos + random.randint(2, 8)
        if pos < len(array):
            array.insert(pos, 0)
    
    print(array)
    return array
    
# EEG TRIGGER (simple)
def trigger(code)
    parallel.setData(code)
    core.wait(0.020)
    parallel.setData(0)

# EEG TRIGGER (read port)
try:
    port = serial.Serial("COM4", 115200)  # COM4 on Mikkel's PC (CHECK!!)
    port_type = 'serial'
except NotImplementedError:
    port = parallel.setPortAddress(0x378) # address for parallel port on many machines (CHECK!!)
    port_type = 'parallel'
except:
    port_type = 'Not set'

print('port type: {}'.format(port_type))

if port_type == 'parallel':
    def trigger(code=1):
        port.setData(code)
        print('trigger sent {}'.format(code))
elif port_type == 'serial':
    def trigger(code=1):
        port.write(code.to_bytes(1, 'big'))
        print('trigger sent {}'.format(code))
else:
    def trigger(code=1):
        print('trigger not sent {}'.format(code))

# RUN TASK
def run_task(n_trials, ratio):
    
    trl_list = make_triallist(n_trials, ratio)

    # Define the standard and deviant sounds
    standard_tone = sound.Sound(1000, sampleRate=44100, secs=0.031, stereo=True)             # Standard tone
    deviant_tone = sound.Sound(1140, octave=4, sampleRate=44100, secs=0.031, stereo=True)    # Deviant tone

    standard_text = visual.TextStim(win, text='Standard', color='blue')
    deviant_text = visual.TextStim(win, text='Deviant', color='red')
    blank_text = visual.TextStim(win, text='', color='red')

    # Trial loop
    for tt, trl in enumerate(trl_list):
        nextFlip = win.getFutureFlipTime()
        if trl == 0:
            deviant_tone.play(when = nextFlip)
            deviant_text.draw()
            trig = 2
        else:
            standard_tone.play(when = nextFlip)
            standard_text.draw()
            trig = 1
          
        win.callOnFlip(trigger, trig)        
        win.flip()                                  # Update the window to show the visual stimulus
        core.wait(0.25)
        blank_text.draw()
        win.flip()
#        core.wait(0.50+random.uniform(0, 0.25))     # Wait between tones with random ISI
        core.wait(0.55)     # Wait 800 ms between tones
        
        # Check for quit (the Esc or q key)
        if event.getKeys(keyList=["escape","q"]):
            core.quit()

    # Close the window
    win.close()
    core.quit()

################################################################################
# RUN
################################################################################
run_task(n_trials, deviant_prob)