from psychopy import visual, core, event, sound, gui
import pandas as pd
import numpy as np
import os

from settings import getSettings
from participant import Participant
from trial import ConvertFreq, MemoryTrial, ProductionTrial, TestTrial
from data_collecter import CollectTrials
from condition_manager import GenerateTrials

path = "Sequence/sequences.csv"
trial_seqs = GenerateTrials(path)

fullscreen, window_size, bg_color, text_color, duration, response_keys = getSettings()
win = visual.Window(size=window_size, color = bg_color, units = "pix")

