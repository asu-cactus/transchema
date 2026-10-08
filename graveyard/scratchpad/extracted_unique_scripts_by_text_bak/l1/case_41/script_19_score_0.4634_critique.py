import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

# Group by 'zipcode' and 'AGI_STUB' and sum 'N1' and 'A00100'
df_grouped = df.groupby(['zipcode', 'AGI_STUB'], as_index=False)[['N1', 'A00100']].sum()

# Ensure correct dtypes
df_grouped = df_grouped.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)