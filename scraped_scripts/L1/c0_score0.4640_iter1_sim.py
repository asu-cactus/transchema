import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)
df = df[['State', 'AverageTemperature']]
df['State'] = df['State'].astype(str)
df['AverageTemperature'] = pd.to_numeric(df['AverageTemperature'], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)