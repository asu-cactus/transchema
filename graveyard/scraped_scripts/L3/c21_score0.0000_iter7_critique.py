import pandas as pd
import re

# Read source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)

# Clean Country column: strip spaces and remove suffixes in parentheses
def clean_country(name):
    if pd.isna(name):
        return name
    # Remove anything in parentheses and trailing spaces
    return re.sub(r'\s*\(.*\)$', '', name).strip()

df['Country'] = df['Country'].apply(clean_country)

# Extract two distinct dt values to split the data
dt_values = df['dt'].dropna().unique()
if len(dt_values) < 2:
    # If less than 2 distinct dt, duplicate the data for both subsets
    dt_x = dt_y = dt_values[0]
else:
    # Sort dt values to pick earliest and latest (or first two)
    dt_values_sorted = sorted(dt_values)
    dt_x, dt_y = dt_values_sorted[0], dt_values_sorted[1]

# Create two subsets filtered by dt_x and dt_y
df_x = df[df['dt'] == dt_x][['Country', 'AverageTemperature']].copy()
df_x = df_x.rename(columns={'AverageTemperature': 'AverageTemperature_x'})

df_y = df[df['dt'] == dt_y][['Country', 'AverageTemperature']].copy()
df_y = df_y.rename(columns={'AverageTemperature': 'AverageTemperature_y'})

# Join on Country
result = pd.merge(df_x, df_y, on='Country', how='inner')

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)