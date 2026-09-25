import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_1.csv", index_col=0)

# Join on Mouse ID
df_merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint, aggregate count distinct Mouse ID as Mouse ID
result = df_merged.groupby(['Drug', 'Timepoint'], as_index=False).agg({'Mouse ID': pd.Series.nunique})

# Rename columns to match target schema exactly
result = result.rename(columns={'Mouse ID': 'Mouse ID'})

# Ensure types match target schema
result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(int)
result['Drug'] = result['Drug'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_39/target_multisource_mcts.csv", index=False)