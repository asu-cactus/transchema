import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_0.csv", index_col=0)
df0['Major_category'] = df0['Major_category'].str.strip()
df0 = df0[df0['Major_category'].notna() & (df0['Major_category'] != '')]
result = df0.groupby('Major_category', as_index=False)['Median'].mean()
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts.csv", index=False)