class BaseTrial:
    def __init__(self, trial_id, learning_condition, trial_spec):
        self.trial_id = trial_id
        self.learning_condition = learning_condition
        self.trial_spec = trial_spec

    def run(self, stimulus_manager, response_manager, data_manager):
        NotImplementedError

#Modellen leverer her en trial spec, altså hvilke specs, der skal bruges for at trial kan udføres.
trial_spec = {
    "learning_condition": "production",
    "first_tone": 60,
    "choice_options": [
        {"left": 62, "right": 64},
        {"left": 65, "right": 67},
        ...
    ],
    "correct_melody": [60, 62, 65, 67, 69, 67, 65, 64],
    "test_melody": [60, 62, 65, 67, 70, 67, 65, 64],
    "changed": True,
    "change_type": "surprising",
    "change_position": 5
}

