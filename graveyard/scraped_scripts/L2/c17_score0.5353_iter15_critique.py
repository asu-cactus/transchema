import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

# Join on 'state'
df = pd.merge(s1, s0[['population', 'state']], on='state', how='inner')

# Ensure correct types as per target schema
df['Broadband Initiative'] = df['Broadband Initiative'].astype(int)
df['Federal'] = df['Federal'].astype(int)
df['Percent'] = df['Percent'].astype(float)
df['state'] = df['state'].astype(str)
df['population'] = df['population'].astype(int)

# Project columns in target schema order
df = df[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)