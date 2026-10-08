import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

# Group by conservation_status and count distinct scientific_name
df = df0.groupby('conservation_status', dropna=False)['scientific_name'].nunique().reset_index()

# Rename columns to match target schema
df.columns = ['conservation_status', 'scientific_name']

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)