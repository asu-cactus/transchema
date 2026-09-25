import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)

df = df0[['State', 'AverageTemperature']].copy()
df['State'] = df['State'].astype(str)
df['AverageTemperature'] = pd.to_numeric(df['AverageTemperature'], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)