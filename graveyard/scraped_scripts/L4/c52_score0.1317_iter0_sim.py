import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Ensure all columns in target schema are present and in correct order
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Some source tables have PolityName as string, target expects integer, so convert if possible
# Try to convert PolityName to numeric, coercing errors to NaN
df_all['PolityName'] = pd.to_numeric(df_all['PolityName'], errors='coerce')

# Convert all columns to appropriate types (integers where possible)
for col in target_cols:
    if col in df_all.columns:
        if col == 'PolityName':
            # PolityName is integer in target, but may have NaNs, keep as float then convert to Int64 (nullable int)
            df_all[col] = df_all[col].astype('Int64')
        elif col == 'Side':
            # Side column in sources is string (e.g., 'A', 'B'), but target examples show integers
            # Map Side letters to integers by factorizing
            if df_all[col].dtype == object:
                df_all[col] = pd.factorize(df_all[col])[0] + 1
            df_all[col] = df_all[col].astype('Int64')
        elif col == 'IsInitiator':
            df_all[col] = df_all[col].astype('Int64')
        elif col == 'Outcome':
            df_all[col] = df_all[col].astype('Int64')
        elif col == 'Deaths':
            # Deaths may be float, convert to Int64 nullable
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')
        else:
            # For year, month, day, WarID, PolityID convert to Int64 nullable
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')
    else:
        # If column missing, create with NaNs
        df_all[col] = pd.NA

df_all = df_all[target_cols]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)