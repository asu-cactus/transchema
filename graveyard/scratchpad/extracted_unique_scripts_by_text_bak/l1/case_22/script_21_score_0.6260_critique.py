import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_2.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2], ignore_index=True)

# GROUP BY 'condition' and aggregate sum of 'click'
result = df_all.groupby('condition', as_index=False)['click'].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)