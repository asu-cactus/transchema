import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df0 = df0.dropna(subset=['conservation_status', 'scientific_name'])

result = df0.groupby('conservation_status', as_index=False)['scientific_name'].nunique()
result.columns = ['conservation_status', 'scientific_name']

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)