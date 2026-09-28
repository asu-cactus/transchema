import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Join s2 with s0 to get PolityName for s2 rows
join_cols = ['WarID', 'PolityID']
join_result = pd.merge(s2, s0[['WarID', 'PolityID', 'PolityName']], on=join_cols, how='left')

# Union s1 and s3 (same schema)
union_1_3 = pd.concat([s1, s3], ignore_index=True)

# Union join_result and union_1_3
combined = pd.concat([join_result, union_1_3], ignore_index=True)

# Map Side from 'A'/'B' to 1/2
combined['Side'] = combined['Side'].map({'A':1, 'B':2})

# Define aggregation functions
agg_dict = {
    'StartYear': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Side': 'first',
    'IsInitiator': 'first',
    'Outcome': 'first',
    'Deaths': 'sum'
}

# Group by PolityName, WarID, PolityID
group_cols = ['PolityName', 'WarID', 'PolityID']

# Perform groupby and aggregation
final_df = combined.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Cast columns to integer types as per target schema
final_df['WarID'] = final_df['WarID'].astype('Int64')
final_df['PolityID'] = final_df['PolityID'].astype('Int64')
final_df['StartYear'] = final_df['StartYear'].astype('Int64')
final_df['StartMonth'] = final_df['StartMonth'].astype('Int64')
final_df['StartDay'] = final_df['StartDay'].astype('Int64')
final_df['EndYear'] = final_df['EndYear'].astype('Int64')
final_df['EndMonth'] = final_df['EndMonth'].astype('Int64')
final_df['EndDay'] = final_df['EndDay'].astype('Int64')
final_df['Side'] = final_df['Side'].astype('Int64')
final_df['IsInitiator'] = final_df['IsInitiator'].astype('Int64')
final_df['Outcome'] = final_df['Outcome'].astype('Int64')
final_df['Deaths'] = final_df['Deaths'].astype('Int64')

# Reorder columns to match target schema exactly
cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

final_df = final_df[cols]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)