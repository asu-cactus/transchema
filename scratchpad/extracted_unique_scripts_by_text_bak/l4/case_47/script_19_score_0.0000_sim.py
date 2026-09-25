import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

union_result = pd.concat([s0, s2], ignore_index=True)

join_result_1 = pd.merge(union_result, s1, on="WarID", how="inner", suffixes=('', '_s1'))

join_result_2 = pd.merge(join_result_1, s3, on="WarID", how="inner", suffixes=('', '_s3'))

df = join_result_2.copy()

# Fill missing IsIntervention and IsInternational with 0 (as per target examples)
df['IsIntervention'] = df['IsIntervention'].fillna(0).astype(int)
df['IsInternational'] = df['IsInternational'].fillna(0).astype(int)

# Ensure WarShortName and WarType come from the unioned tables (no conflict expected)
# WarShortName and WarType columns exist in all sources, keep from union_result (or join_result_2)
# They should be consistent, but keep from join_result_2 to have all columns aligned

# Select and reorder columns as per target schema
result = df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

# Group by all columns to remove duplicates if any (as per GROUP_BY)
result = result.groupby(['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational'], as_index=False).size()

# Drop the size column (count) as target schema does not have it
result = result.drop(columns=['size'])

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)