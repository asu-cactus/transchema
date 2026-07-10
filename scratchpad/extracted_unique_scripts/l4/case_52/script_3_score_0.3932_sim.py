import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv",
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Ensure all target columns exist, fill missing PolityName in Source3 with NaN
if 'PolityName' not in df_all.columns:
    df_all['PolityName'] = pd.NA

# Convert PolityName to integer if possible, else keep as is (target expects integer)
# But PolityName looks like string names in sources, target example shows integer values.
# Since source PolityName is string, but target expects integer, we convert PolityName to categorical codes.
df_all['PolityName'] = df_all['PolityName'].astype('category').cat.codes.replace(-1, pd.NA)

# Convert Side from string to integer if needed
# Source Side is string like 'A', 'B', target Side is integer (e.g. 716, 549)
# But target examples show Side as integer, but source Side is string labels.
# We convert Side to categorical codes as integer
df_all['Side'] = df_all['Side'].astype('category').cat.codes.replace(-1, pd.NA)

# Ensure all columns in target schema exist and are in correct order
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Some columns may be missing in some sources, ensure all exist
for col in target_cols:
    if col not in df_all.columns:
        df_all[col] = pd.NA

# Cast columns to appropriate types (integers where possible)
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    # Convert to numeric, coerce errors to NaN, then to Int64 (nullable integer)
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

df_all = df_all[target_cols]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)