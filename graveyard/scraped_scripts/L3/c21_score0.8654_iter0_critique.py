import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)

grouped = df0.groupby('Country', as_index=False).agg({'AverageTemperature': 'mean'})

grouped = grouped.rename(columns={'AverageTemperature': 'AverageTemperature_x'})

grouped['AverageTemperature_y'] = grouped['AverageTemperature_x'] * -1

result = grouped[['Country', 'AverageTemperature_x', 'AverageTemperature_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)