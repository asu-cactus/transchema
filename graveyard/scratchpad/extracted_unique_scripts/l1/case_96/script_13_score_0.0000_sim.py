import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0['Publisher'] = df0['Publisher'].astype(str).str.strip()
publisher_counts = df0['Publisher'].value_counts().reset_index()
publisher_counts.columns = ['Publisher', 'count']

publisher_counts['Publisher'] = publisher_counts['Publisher'].astype(int, errors='ignore')
publisher_counts = publisher_counts[publisher_counts['Publisher'].apply(lambda x: isinstance(x, int))]

publisher_counts = publisher_counts.sort_values('Publisher').reset_index(drop=True)

publisher_counts.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)