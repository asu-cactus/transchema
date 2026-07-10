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

# Ensure all columns exist in all dataframes (Source3 lacks PolityName)
if 'PolityName' not in df_all.columns:
    df_all['PolityName'] = pd.NA

# Convert PolityName to integer if possible, else leave as is (target expects integer)
# The target example shows PolityName as integer, but source has string names.
# We must convert PolityName to integer. Since source PolityName is string, we encode it as categorical codes.
df_all['PolityName'] = df_all['PolityName'].astype('category').cat.codes.replace(-1, pd.NA)

# Convert Side to integer similarly (source Side is string like 'A', 'B', target Side is integer)
df_all['Side'] = df_all['Side'].astype('category').cat.codes.replace(-1, pd.NA)

# Convert all columns to target types:
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    if col in df_all.columns:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# PIVOT and GROUP_BY IsInitiator:
# The partial plan says PIVOT and GROUP_BY on IsInitiator.
# But the target schema includes IsInitiator as a column, so no pivoting to widen the table is needed.
# Instead, we keep IsInitiator as a grouping column.
# The data is already in the correct shape, so just group by all columns except those that need aggregation.
# But the target examples show no aggregation, so we keep rows as is.

# Since the target examples show no aggregation, and the source data is already in the correct shape,
# we just ensure the columns are in the correct order and save.

target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_out = df_all[target_cols]

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)