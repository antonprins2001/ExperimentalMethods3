from psychopy import visual, core, event
import pandas as pd

from settings import Settings
from participant import Participant
from block import Block
from trial import Trial
from data_collecter import DataManager
from condition_manager import GenerateTrials

path = "Sequence/sequences.csv"
trial_seqs = GenerateTrials(path)
