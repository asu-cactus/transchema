import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

df = df0.copy()
df = df.drop(columns=['Origin', 'Month'])
df = df.rename(columns={'Value': 'Year'})

df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)

df = df[['Country / territory of asylum/residence', 'Year']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)