import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source4_45_0 and Source4_45_1
union_0_1 = pd.concat([s0, s1], ignore_index=True)

# JOIN Source4_45_2 and Source4_45_3 on WarID
join_2_3 = pd.merge(s2, s3, on="WarID", how="inner")

# JOIN union_0_1 with join_2_3 on WarID
final_join = pd.merge(union_0_1, join_2_3, on="WarID", how="inner")

# GROUP BY the leftmost columns of target schema and count WarID
grouped = final_join.groupby(
    ['WarType_x', 'WarID', 'WarShortName_x', 'IsInternational', 'IsIntervention'],
    as_index=False
).agg({'WarID': 'count'})

# Rename columns to match target schema
grouped.rename(
    columns={
        'WarType_x': 'WarType',
        'WarShortName_x': 'WarShortName',
        'WarID': 'WarID',  # WarID is both group key and aggregation column, keep group key
        'IsInternational': 'IsInternational',
        'IsIntervention': 'IsIntervention'
    },
    inplace=True
)

# The aggregation column 'WarID' count is currently in 'WarID' column, but that conflicts with group key WarID.
# We need to replace the count column with the count of WarID per group, but keep WarID as group key.
# So we rename the count column to a temporary name and then drop it, because target examples show counts in WarID column.
# Actually, target schema has WarID as integer key, and WarShortName as integer (count), so the target examples show counts in WarID and WarShortName columns.
# So we must assign counts to WarID and WarShortName columns accordingly.

# From target examples:
# ['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']
# Examples: [1, 95, 95, 0, 0] means WarID=95 is count, WarShortName=95 is count, so both WarID and WarShortName columns are counts.

# So we must aggregate counts for WarID and WarShortName columns.

# Let's do aggregation counts for WarID and WarShortName columns separately.

# Re-aggregate with counts for WarID and WarShortName columns:

agg_df = final_join.groupby(
    ['WarType_x', 'IsInternational', 'IsIntervention'],
    as_index=False
).agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName_x', 'count')
)

# WarType_x is from union_0_1, IsInternational and IsIntervention from join_2_3

# Rename WarType_x to WarType
agg_df.rename(columns={'WarType_x': 'WarType'}, inplace=True)

# Add IsInternational and IsIntervention columns as integers (already integers)

# Final columns order as target schema
result = agg_df[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)