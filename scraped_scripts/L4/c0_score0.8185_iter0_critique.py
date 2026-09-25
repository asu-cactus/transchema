import pandas as pd

# Read all sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

# Join df0 and df1 on COD_PERSONA
df01 = pd.merge(df0, df1, on="COD_PERSONA", how="inner")

# Join df01 and df2 on COD_PERSONA and COD_IDCONTRA
df012 = pd.merge(df01, df2, on=["COD_PERSONA", "COD_IDCONTRA"], how="inner")

# Join df012 and df3 on COD_OFICIPAL (df0) and COD_OFICI (df3)
df0123 = pd.merge(df012, df3, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

# Select distinct des_territ
result = df0123[["des_territ"]].drop_duplicates().reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)