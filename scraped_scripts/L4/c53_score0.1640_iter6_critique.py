import pandas as pd

# Read sources with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv', index_col=0)

# Source2 lacks PolityName, add it with NaN to align schemas
source2['PolityName'] = pd.NA

# Reorder columns to match target schema order exactly
# Target schema order:
# ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
#  'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

cols_order = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# Ensure all sources have these columns in this order
source0 = source0[cols_order]
source1 = source1[cols_order]
source2 = source2[cols_order]
source3 = source3[cols_order]

# Union all sources
df = pd.concat([source0, source1, source2, source3], ignore_index=True)

# Convert columns to appropriate types matching target schema
# PolityName: string
df['PolityName'] = df['PolityName'].astype('string')

# The rest are integers, but source data may have floats or NaNs, convert carefully
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# For Deaths, sum aggregation will handle NaNs as zero, but convert to float first
for col in int_cols:
    # For Deaths, keep float for sum, others convert to Int64 (nullable integer)
    if col == 'Deaths':
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Group by all columns except Deaths, aggregate Deaths by sum
group_by_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome']

agg_dict = {'Deaths': 'sum'}

df_grouped = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# After aggregation, convert Deaths to Int64 (nullable int)
df_grouped['Deaths'] = df_grouped['Deaths'].round().astype('Int64')

# Reorder columns to target schema order
df_grouped = df_grouped[cols_order]

# Write output CSV without index
df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv', index=False)