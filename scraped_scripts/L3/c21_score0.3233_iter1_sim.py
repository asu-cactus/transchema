import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="Country", suffixes=('_x', '_y'))

result = df_joined[['Country', 'AverageTemperature_x', 'AverageTemperature_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)