import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Ensure 'month' is integer
df_all['month'] = pd.to_numeric(df_all['month'], errors='coerce').fillna(0).astype(int)

# Group by 'month' and count rows
grouped = df_all.groupby('month', dropna=False, as_index=False).size().rename(columns={'size': 'count'})

# The target schema is ['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']
# All columns are integer and in examples all columns have the same value per row (the count)
# So create a DataFrame with all columns equal to the count

result = pd.DataFrame()
result['month'] = grouped['month']
for col in ['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']:
    result[col] = grouped['count']

# Convert all columns to int
result = result.astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)