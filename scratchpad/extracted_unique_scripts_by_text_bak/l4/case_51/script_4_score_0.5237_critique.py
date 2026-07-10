import pandas as pd

# Read all source CSVs with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Add missing PolityName column to source1 with NaNs to align schemas for union
if 'PolityName' not in source1.columns:
    source1['PolityName'] = pd.NA

# Ensure consistent column order for union
cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# Reorder columns for all sources
source0 = source0[cols]
source1 = source1[cols]
source2 = source2[cols]
source3 = source3[cols]

# Union all sources (concatenate)
df = pd.concat([source0, source1, source2, source3], ignore_index=True)

# Group by the leftmost columns of target schema: Side, WarID, PolityID
group_cols = ['Side', 'WarID', 'PolityID']

# Define aggregation dictionary
# For PolityName: count distinct (number of unique non-null PolityName)
# For Deaths: sum
# For other columns: min (to get consistent integer values, ignoring NaNs)
agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'min',
    'EndMonth': 'min',
    'EndDay': 'min',
    'IsInitiator': 'min',
    'Outcome': 'min',
    'Deaths': 'sum',
    'PolityName': lambda x: x.nunique(dropna=True)
}

grouped = df.groupby(group_cols).agg(agg_dict).reset_index()

# Cast columns to integer as per target schema
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

for col in int_cols:
    # Some columns may have NaNs after aggregation, fill with 0 before casting
    grouped[col] = grouped[col].fillna(0).astype(int)

# Reorder columns to match target schema exactly
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

grouped = grouped[target_cols]

# Write output CSV without index
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)