import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Union s0, s1, s3 (same schema)
union_013 = pd.concat([s0, s1, s3], ignore_index=True, sort=False)

# Join union_013 with s2 on WarID and PolityID (inner join to avoid unmatched rows)
joined = pd.merge(union_013, s2.drop(columns=['StartYear','StartMonth','StartDay','EndYear','EndMonth','EndDay','Side','IsInitiator','Outcome','Deaths']), 
                  on=['WarID','PolityID'], how='inner', suffixes=('', '_s2'))

# After join, keep columns from union_013 plus PolityName from union_013 (already present)
# The join was only to ensure matching keys; s2 columns dropped except keys

# Map Side from 'A'/'B' to 1/2, keep NaN as is for now
joined['Side'] = joined['Side'].map({'A':1, 'B':2})

# Fill NaNs in month/day columns with 0 before aggregation
for col in ['StartMonth', 'StartDay', 'EndMonth', 'EndDay']:
    joined[col] = joined[col].fillna(0)

# PolityName is string, ensure no leading/trailing spaces (string operator)
joined['PolityName'] = joined['PolityName'].astype(str).str.strip()

# Group by PolityName, WarID, PolityID
agg_dict = {
    'StartYear': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'Side': 'first',
    'IsInitiator': 'first',
    'Outcome': 'first',
    'Deaths': 'sum'
}

final = joined.groupby(['PolityName', 'WarID', 'PolityID'], dropna=False, as_index=False).agg(agg_dict)

# Convert types to match target schema
final['WarID'] = final['WarID'].astype('Int64')
final['PolityID'] = final['PolityID'].astype('Int64')
final['StartYear'] = final['StartYear'].astype('Int64')
final['StartMonth'] = final['StartMonth'].astype('Int64')
final['StartDay'] = final['StartDay'].astype('Int64')
final['EndYear'] = final['EndYear'].astype('Int64')
final['EndMonth'] = final['EndMonth'].astype('Int64')
final['EndDay'] = final['EndDay'].astype('Int64')
final['Side'] = final['Side'].astype('Int64')
final['IsInitiator'] = final['IsInitiator'].astype('Int64')
final['Outcome'] = final['Outcome'].astype('Int64')
final['Deaths'] = final['Deaths'].astype('Int64')

# PolityName as string (already stripped)
final['PolityName'] = final['PolityName'].astype(str)

# Reorder columns exactly as target schema
final = final[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)