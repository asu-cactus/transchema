import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_1.csv", index_col=0)

# Join on Mouse ID
merged = pd.merge(df0, df1, on="Mouse ID", how='inner')

# Group by Drug and Timepoint, aggregate count distinct Mouse ID as Mouse ID count
result = merged.groupby(['Drug', 'Timepoint'], as_index=False).agg({'Mouse ID': pd.Series.nunique})

# Rename columns to match target schema exactly
result = result.rename(columns={'Mouse ID': 'Mouse ID'})

# Convert types to match target schema
result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_74/target_multisource_mcts.csv", index=False)