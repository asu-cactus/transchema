import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

# Join df0 and df3 on COD_OFICIPAL = COD_OFICI and COD_AREANEGO = cod_areanego
df0_3 = pd.merge(df0, df3, left_on=['COD_OFICIPAL', 'COD_AREANEGO'], right_on=['COD_OFICI', 'cod_areanego'], how='inner')

# Join with df1 on COD_PERSONA
df0_3_1 = pd.merge(df0_3, df1, on='COD_PERSONA', how='inner')

# Join with df2 on COD_PERSONA
df_all = pd.merge(df0_3_1, df2, on='COD_PERSONA', how='inner')

# Select des_territ, drop NaNs and duplicates
result = df_all[['des_territ']].dropna(subset=['des_territ']).drop_duplicates().reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)