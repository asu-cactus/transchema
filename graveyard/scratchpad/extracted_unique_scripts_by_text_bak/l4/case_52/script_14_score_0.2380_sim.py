import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

cols_target = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Some source tables have PolityName as string, target expects integer, so convert if possible
# But target example shows PolityName as integer, so try to convert PolityName to numeric if possible
# If conversion fails, keep NaN
df_all['PolityName'] = pd.to_numeric(df_all['PolityName'], errors='coerce')

# Ensure all columns exist in df_all, if missing add with NaN
for c in cols_target:
    if c not in df_all.columns:
        df_all[c] = pd.NA

df_all = df_all[cols_target]

# Convert all columns to integer type where possible, else keep as is (NaN will remain)
for c in cols_target:
    df_all[c] = pd.to_numeric(df_all[c], errors='coerce').astype('Int64')

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)