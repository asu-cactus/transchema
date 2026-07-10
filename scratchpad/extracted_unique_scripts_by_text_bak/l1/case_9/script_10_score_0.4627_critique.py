import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

# Select relevant columns
df_selected = df[['zipcode', 'AGI_STUB', 'N1', 'A00100']].copy()

# Ensure correct types
df_selected = df_selected.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

# Group by zipcode and AGI_STUB, aggregate sum on N1 and A00100
df_grouped = df_selected.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({'N1': 'sum', 'A00100': 'sum'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)