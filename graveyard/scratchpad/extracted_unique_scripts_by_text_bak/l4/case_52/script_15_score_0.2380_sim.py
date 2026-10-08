import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Ensure all columns exist in all rows, fill missing columns with NaN
expected_cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
for col in expected_cols:
    if col not in df_all.columns:
        df_all[col] = pd.NA

df_all = df_all[expected_cols]

# Convert columns to appropriate types
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    if col in df_all.columns:
        # PolityName is string in source but target expects integer, convert by factorizing
        if col == 'PolityName':
            df_all[col] = pd.factorize(df_all[col].astype(str))[0]
        else:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce').astype('Int64')

# Pivot on IsInitiator is ambiguous here because IsInitiator is a binary flag, but the partial plan says PIVOT and GROUP_BY on IsInitiator.
# The target schema includes IsInitiator as a column, so no pivoting to widen the table is needed.
# Instead, we keep IsInitiator as a grouping key.

# Group by all columns except PolityName (which is now integer factorized) and aggregate by first or sum where appropriate
# But since the target examples show no aggregation, just keep rows as is.

# Remove duplicates if any
df_all = df_all.drop_duplicates()

# Reorder columns to target schema order
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_all = df_all[target_cols]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)