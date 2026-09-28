import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)

# Clean Country column by removing trailing parentheses and spaces
df0['Country'] = df0['Country'].str.replace(r'\s*\(.*\)$', '', regex=True).str.strip()

# Convert dt to datetime
df0['dt'] = pd.to_datetime(df0['dt'], errors='coerce')

# Filter by dt
df_recent = df0[df0['dt'] >= pd.Timestamp('1900-01-01')]
df_old = df0[df0['dt'] < pd.Timestamp('1900-01-01')]

# Aggregate mean AverageTemperature by Country
df_recent_agg = df_recent.groupby('Country', as_index=False)['AverageTemperature'].mean()
df_recent_agg = df_recent_agg.rename(columns={'AverageTemperature': 'AverageTemperature_x'})

df_old_agg = df_old.groupby('Country', as_index=False)['AverageTemperature'].mean()
df_old_agg = df_old_agg.rename(columns={'AverageTemperature': 'AverageTemperature_y'})

# Join on Country
result = pd.merge(df_recent_agg, df_old_agg, on='Country', how='inner')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)