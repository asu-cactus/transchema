import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

cols_target = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_all = df_all[cols_target]

for col in ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']:
    if col in ['PolityName', 'Side']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)
    else:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)