import pandas as pd

# Read sources with index_col=0
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv', index_col=0)

# Add PolityName column to source1 (which lacks it) with NaN
source1['PolityName'] = pd.NA

# Ensure all sources have the same columns in the same order as target schema (except Side, WarID, PolityID are first)
# Target schema: ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# Reorder columns accordingly
cols_order = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

# For source1, columns are missing PolityName, so we added it
source0 = source0[cols_order]
source1 = source1[cols_order]
source2 = source2[cols_order]
source3 = source3[cols_order]

# Concatenate all sources (UNION)
df_all = pd.concat([source0, source1, source2, source3], ignore_index=True)

# Group by leftmost columns: Side, WarID, PolityID
group_cols = ['Side', 'WarID', 'PolityID']

# Aggregations:
# sum for numeric columns except group by columns and PolityName
sum_cols = ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay',
            'IsInitiator', 'Outcome', 'Deaths']

# For PolityName, count distinct (number of unique PolityName per group)
# PolityName is string, so count distinct non-null values

agg_dict = {col: 'sum' for col in sum_cols}
agg_dict['PolityName'] = lambda x: x.nunique(dropna=True)

df_grouped = df_all.groupby(group_cols).agg(agg_dict).reset_index()

# Convert columns to integer as per target schema
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    # Some columns may have NaN after aggregation, fill with 0 before converting
    df_grouped[col] = df_grouped[col].fillna(0).astype(int)

# Write to target file
df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv', index=False)