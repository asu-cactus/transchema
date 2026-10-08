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

# Ensure all columns are present and in target order
target_cols = ['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']

df = df[target_cols]

# Convert all columns to integer type where possible, else keep as is
for col in target_cols:
    if col in ['Deaths']:
        # Deaths may have NaNs and floats, convert to Int64 (nullable integer)
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    elif col in ['StartMonth', 'StartDay', 'EndMonth', 'EndDay']:
        # These may have NaNs, convert to Int64 nullable integer
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    else:
        # For other columns, convert to integer (nullable)
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)