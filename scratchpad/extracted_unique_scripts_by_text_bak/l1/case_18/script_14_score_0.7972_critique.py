import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

# Group by 'y' and aggregate by mean for each feature column
df_grouped = df0.groupby('y', as_index=False).mean()

# Convert feature columns to int as in target schema
for col in df_grouped.columns:
    if col != 'y':
        df_grouped[col] = df_grouped[col].round().astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)