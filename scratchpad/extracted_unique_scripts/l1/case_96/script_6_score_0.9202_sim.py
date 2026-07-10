import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0_subset = df0[['Publisher']].copy()
df1_subset = df1[['hero_names']].copy()
df1_subset['Publisher'] = pd.NA

union_df = pd.concat([df0_subset, df1_subset[['Publisher']]], ignore_index=True)

publisher_counts = union_df['Publisher'].value_counts(dropna=True).reset_index()
publisher_counts.columns = ['Publisher', 'count']
publisher_counts['Publisher'] = publisher_counts['Publisher'].astype(str)
publisher_counts['count'] = publisher_counts['count'].astype(int)

publisher_counts.rename(columns={'count': 'Publisher'}, inplace=True)

publisher_counts.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)