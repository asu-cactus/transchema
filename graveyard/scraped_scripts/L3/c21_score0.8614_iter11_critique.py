import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv', index_col=0)
df['dt'] = pd.to_datetime(df['dt'])
median_dt = df['dt'].median()

df1 = df[df['dt'] < median_dt]
df2 = df[df['dt'] >= median_dt]

agg1 = df1.groupby('Country', as_index=False)['AverageTemperature'].mean()
agg2 = df2.groupby('Country', as_index=False)['AverageTemperature'].mean()

agg1.rename(columns={'AverageTemperature': 'AverageTemperature_x'}, inplace=True)
agg2.rename(columns={'AverageTemperature': 'AverageTemperature_y'}, inplace=True)

result = pd.merge(agg1, agg2, on='Country')
result.to_csv('autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv', index=False)