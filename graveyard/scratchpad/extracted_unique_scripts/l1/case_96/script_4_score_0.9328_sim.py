import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0['Publisher'] = df0['Publisher'].astype(str).str.strip()
publisher_counts = df0.groupby('Publisher').size().reset_index(name='count')

publisher_counts['Publisher'] = pd.factorize(publisher_counts['Publisher'])[0] + 1

publisher_counts.rename(columns={'count': 'Publisher'}, inplace=True)

publisher_counts.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)