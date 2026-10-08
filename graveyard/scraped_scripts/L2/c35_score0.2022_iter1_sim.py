import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv", index_col=0)

df0_sub = df0[['Date', 'ResultDir', 'ResultSpeed']].copy()
df0_sub.rename(columns={'ResultSpeed': 'NumMosquitos'}, inplace=True)
df0_sub['ResultDir'] = pd.to_numeric(df0_sub['ResultDir'], errors='coerce')
df0_sub['NumMosquitos'] = pd.to_numeric(df0_sub['NumMosquitos'], errors='coerce')
df0_sub['Date'] = df0_sub['Date'].astype(str)

df1_sub = df1[['Date', 'ResultDir', 'NumMosquitos']].copy() if 'ResultDir' in df1.columns else df1[['Date', 'NumMosquitos']].copy()
if 'ResultDir' not in df1_sub.columns:
    df1_sub['ResultDir'] = pd.NA
df1_sub['ResultDir'] = pd.to_numeric(df1_sub['ResultDir'], errors='coerce')
df1_sub['NumMosquitos'] = pd.to_numeric(df1_sub['NumMosquitos'], errors='coerce')
df1_sub['Date'] = df1_sub['Date'].astype(str)

df_target = pd.concat([df0_sub, df1_sub], ignore_index=True, sort=False)
df_target = df_target[['Date', 'ResultDir', 'NumMosquitos']]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_35/target_multisource_mcts.csv", index=False)