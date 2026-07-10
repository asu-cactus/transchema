import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

dfs = [df0, df1, df2, df3]

for i, df in enumerate(dfs):
    if 'PolityName' not in df.columns:
        df['PolityName'] = pd.NA
    # Ensure consistent dtypes for PolityID and PolityName
    df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
    if df['PolityName'].dtype != 'string':
        df['PolityName'] = df['PolityName'].astype('string')
    # Convert Side to string if not already
    if df['Side'].dtype != 'string':
        df['Side'] = df['Side'].astype('string')
    # Convert other columns to numeric with Int64 dtype where appropriate
    for col in ['WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df_all = pd.concat(dfs, ignore_index=True)

# Reorder columns to target schema and ensure types
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']
df_all = df_all[target_cols]

# PolityName in target schema is integer according to prompt, but source has string.
# We convert PolityName string to integer by encoding categories (consistent with examples).
# If PolityName is missing, it will be NaN after conversion.
df_all['PolityName'] = df_all['PolityName'].astype('category').cat.codes.replace(-1, pd.NA).astype('Int64')

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)