import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0, parse_dates=['dt'])

median_dt = df0['dt'].median()

df_filtered = df0[df0['dt'] < median_dt]

df_left = df_filtered.rename(columns={'AverageTemperature': 'AverageTemperature_x'})
df_right = df_filtered.rename(columns={'AverageTemperature': 'AverageTemperature_y'})

df_joined = pd.merge(df_left[['Country', 'AverageTemperature_x']],
                     df_right[['Country', 'AverageTemperature_y']],
                     on='Country')

df_joined.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)