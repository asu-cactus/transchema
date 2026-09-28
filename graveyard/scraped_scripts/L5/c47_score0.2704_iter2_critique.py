import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert PolityName and Initiator to integer codes (consistent with target schema)
df['PolityName'] = df['PolityName'].astype('category').cat.codes
df['Initiator'] = df['Initiator'].astype('category').cat.codes

# Define target columns and group by columns
target_cols = ['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']

# Keep only target columns
df = df[target_cols]

# Convert all columns to numeric with nullable integer type where possible
for col in target_cols:
    if col == 'Deaths':
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    elif col in ['StartMonth', 'StartDay', 'EndMonth', 'EndDay']:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Group by Outcome and WarID, aggregate sum on other columns
agg_cols = [col for col in target_cols if col not in ['Outcome', 'WarID']]
df_agg = df.groupby(['Outcome', 'WarID'], dropna=False)[agg_cols].sum(min_count=1).reset_index()

# Reorder columns to target schema order
df_agg = df_agg[target_cols]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)