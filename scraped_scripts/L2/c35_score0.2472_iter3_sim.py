import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv", index_col=0)

df0_sub = df0[['Date', 'ResultDir']].copy()
df1_sub = df1[['Date', 'NumMosquitos']].copy()

df0_sub['NumMosquitos'] = pd.NA
df1_sub['ResultDir'] = pd.NA

df_union = pd.concat([df0_sub, df1_sub], ignore_index=True)

df_grouped = df_union.groupby('Date', as_index=False).agg({
    'ResultDir': 'mean',
    'NumMosquitos': 'mean'
})

df_grouped['Date'] = df_grouped['Date'].astype(str)
df_grouped['ResultDir'] = pd.to_numeric(df_grouped['ResultDir'], errors='coerce')
df_grouped['NumMosquitos'] = pd.to_numeric(df_grouped['NumMosquitos'], errors='coerce')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_35/target_multisource_mcts.csv", index=False)