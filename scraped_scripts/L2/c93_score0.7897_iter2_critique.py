import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_1.csv", index_col=0)

# Join on Mouse ID
df_merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint, aggregate count of Mouse ID
result = df_merged.groupby(['Drug', 'Timepoint'], as_index=False).agg({'Mouse ID': 'count'})

# Ensure column types match target schema
result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_93/target_multisource_mcts.csv", index=False)