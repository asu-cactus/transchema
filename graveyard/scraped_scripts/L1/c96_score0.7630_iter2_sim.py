import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0['Publisher'] = df0['Publisher'].astype(str).str.strip()
publisher_counts = df0.groupby('Publisher').size().reset_index(name='count')

publisher_to_int = {pub: i+1 for i, pub in enumerate(sorted(publisher_counts['Publisher']))}
publisher_counts['Publisher'] = publisher_counts['Publisher'].map(publisher_to_int)

publisher_counts = publisher_counts.rename(columns={'Publisher': 'Publisher'})

publisher_counts[['Publisher']].to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)