import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)
df = df0[['Country / territory of asylum/residence', 'Year']].copy()
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)