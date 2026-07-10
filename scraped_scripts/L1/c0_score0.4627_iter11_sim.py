import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)
df_filtered = df0[df0['Country'] == 'Russia']
result = df_filtered[['State', 'AverageTemperature']].copy()
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)