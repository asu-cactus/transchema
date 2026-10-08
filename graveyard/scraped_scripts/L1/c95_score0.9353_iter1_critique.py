import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

# Ensure correct types
df0['customer_id'] = df0['customer_id'].astype(int)
df0['date'] = df0['date'].astype(str)

# Group by customer_id and aggregate date by minimum (earliest) date
df_target = df0.groupby('customer_id', as_index=False).agg({'date': 'min'})

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)