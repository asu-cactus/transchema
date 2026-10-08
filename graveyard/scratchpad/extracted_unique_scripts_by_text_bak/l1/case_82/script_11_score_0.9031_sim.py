import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df = df0[['conservation_status', 'scientific_name']].copy()
df = df.dropna(subset=['conservation_status'])

result = df.groupby('conservation_status', as_index=False).agg({'scientific_name':'count'})
result = result.rename(columns={'conservation_status':'conservation_status', 'scientific_name':'scientific_name'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)