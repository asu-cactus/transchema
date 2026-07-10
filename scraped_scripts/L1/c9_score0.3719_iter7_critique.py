import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

# Group by STATEFIPS and AGI_STUB, sum N1 and A00100
df_grouped = df.groupby(['STATEFIPS', 'AGI_STUB'], as_index=False)[['N1', 'A00100']].sum()

# Rename STATEFIPS to zipcode to match target schema
df_grouped = df_grouped.rename(columns={'STATEFIPS': 'zipcode'})

# Cast columns to int64 as in target schema
df_grouped = df_grouped.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)