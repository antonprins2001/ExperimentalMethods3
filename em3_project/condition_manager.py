import pandas as pd

def GenerateTrials(path):
    df_order = pd.read_csv(path)
    df = df_order.sample(frac=1)
    trial_data = []
    for i in range(len(df.index)):
        trial = df.loc[0].to_dict()
        trial["trial"] = i
        trial_data.append(trial)
    return trial_data