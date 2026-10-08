import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source0 and Source1
union_0_1 = pd.concat([s0, s1], ignore_index=True)

# GROUP BY WarType in union_0_1: count WarID and WarShortName
union_0_1_grouped = union_0_1.groupby('WarType').agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName', 'count')
).reset_index()

# GROUP BY WarType in s2: count WarID and IsIntervention
s2_grouped = s2.groupby('WarType').agg(
    WarID_s2=('WarID', 'count'),
    IsIntervention=('IsIntervention', 'count')
).reset_index()

# GROUP BY WarType in s3: count WarID and IsInternational
s3_grouped = s3.groupby('WarType').agg(
    WarID_s3=('WarID', 'count'),
    IsInternational=('IsInternational', 'count')
).reset_index()

# Join union_0_1_grouped and s2_grouped on WarType
joined_01_2 = pd.merge(union_0_1_grouped, s2_grouped[['WarType', 'IsIntervention']], on='WarType', how='outer')

# Join the above with s3_grouped on WarType
final_df = pd.merge(joined_01_2, s3_grouped[['WarType', 'IsInternational']], on='WarType', how='outer')

# Fill NaN with 0 for counts
final_df['WarID'] = final_df['WarID'].fillna(0).astype(int)
final_df['WarShortName'] = final_df['WarShortName'].fillna(0).astype(int)
final_df['IsIntervention'] = final_df['IsIntervention'].fillna(0).astype(int)
final_df['IsInternational'] = final_df['IsInternational'].fillna(0).astype(int)

# Reorder columns as per target schema: ['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']
final_df = final_df[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Save to CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)