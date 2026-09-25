import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)

# Convert dt to datetime for filtering
df0['dt'] = pd.to_datetime(df0['dt'], errors='coerce')

# Split into two subsets by date
df_x = df0[df0['dt'] < '1900-01-01'].groupby('Country', as_index=False)['AverageTemperature'].mean()
df_y = df0[df0['dt'] >= '1900-01-01'].groupby('Country', as_index=False)['AverageTemperature'].mean()

# Rename columns to match target schema
df_x = df_x.rename(columns={'AverageTemperature': 'AverageTemperature_x'})
df_y = df_y.rename(columns={'AverageTemperature': 'AverageTemperature_y'})

# Join on Country
result = pd.merge(df_x, df_y, on='Country', how='inner')

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)