import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

# Select only the columns needed for the target schema
df_out = df0[['customer_id', 'date']].copy()

# Ensure types match target schema: customer_id as int, date as string
df_out['customer_id'] = df_out['customer_id'].astype(int)
df_out['date'] = df_out['date'].astype(str)

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)