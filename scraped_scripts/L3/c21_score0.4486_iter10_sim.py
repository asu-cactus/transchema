import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

df_joined = pd.merge(df, df, on=['Country', 'dt'], suffixes=('_x', '_y'))

result = df_joined[['Country', 'AverageTemperature_x', 'AverageTemperature_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)