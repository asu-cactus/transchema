import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

# Select only the target columns
df_selected = df0[['customer_id', 'date']]

# Group by customer_id and date to remove duplicates (no aggregation needed)
df_grouped = df_selected.drop_duplicates()

# Ensure correct types
df_grouped['customer_id'] = df_grouped['customer_id'].astype(int)
df_grouped['date'] = df_grouped['date'].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)