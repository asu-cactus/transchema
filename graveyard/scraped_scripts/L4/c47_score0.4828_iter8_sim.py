import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

pivot_result = src0.pivot(index='WarID', columns='WarShortName', values='WarType').reset_index()

union_result = pd.concat([src1[['WarID', 'IsIntervention']], src3[['WarID', 'IsInternational']]], axis=0, ignore_index=True)

# union_result has different columns, so we need to merge them carefully
# We want to join pivot_result with src1 and src3 on WarID to get all columns

# Merge pivot_result with src1 on WarID to get IsIntervention
merged_1 = pd.merge(pivot_result, src1[['WarID', 'IsIntervention']], on='WarID', how='left')

# Merge the above with src3 on WarID to get IsInternational
merged_2 = pd.merge(merged_1, src3[['WarID', 'IsInternational']], on='WarID', how='left')

# For rows missing IsIntervention or IsInternational, fill with 0 as per target examples
merged_2['IsIntervention'] = merged_2['IsIntervention'].fillna(0).astype(int)
merged_2['IsInternational'] = merged_2['IsInternational'].fillna(0).astype(int)

# The target schema is ['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']
# We need to unpivot the pivoted columns (WarShortName columns) back to rows to get WarShortName and WarType columns

warshortname_cols = [col for col in merged_2.columns if col not in ['WarID', 'IsIntervention', 'IsInternational']]

melted = merged_2.melt(id_vars=['IsIntervention', 'WarID', 'IsInternational'], value_vars=warshortname_cols,
                       var_name='WarShortName', value_name='WarType')

# Drop rows where WarType is NaN (no data)
melted = melted.dropna(subset=['WarType'])

# Convert WarShortName to integer if possible, else keep as is
# From examples, WarShortName is integer in target, but source WarShortName is string
# The examples show WarShortName as integer equal to WarID, so we convert WarShortName to WarID integer if possible
# But since WarShortName is string, and target expects integer, we will convert WarShortName to WarID integer (as in examples)
# So set WarShortName = WarID to match target examples

melted['WarShortName'] = melted['WarID'].astype(int)
melted['WarType'] = melted['WarType'].astype(int)
melted['IsIntervention'] = melted['IsIntervention'].astype(int)
melted['IsInternational'] = melted['IsInternational'].astype(int)
melted['WarID'] = melted['WarID'].astype(int)

final = melted[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)