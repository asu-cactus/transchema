import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0, parse_dates=['dt'])
subset1 = df0[df0['dt'] >= pd.Timestamp('1900-01-01')]

grouped = subset1.groupby('Country', as_index=False).agg({
    'AverageTemperature': 'mean'
}).rename(columns={'AverageTemperature': 'AverageTemperature_x'})

grouped['AverageTemperature_y'] = grouped['AverageTemperature_x']

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)