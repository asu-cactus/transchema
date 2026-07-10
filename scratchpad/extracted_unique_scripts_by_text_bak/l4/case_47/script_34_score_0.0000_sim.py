import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

union_source = pd.concat([df0, df2], ignore_index=True)

joined = pd.merge(union_source, df1[['WarID', 'IsIntervention']], on='WarID', how='left')

grouped = joined.groupby(['IsIntervention', 'WarID', 'WarShortName', 'WarType'], as_index=False).size()

result = grouped.rename(columns={'size': 'Count'})

# The target schema is ['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']
# We have no IsInternational info yet, so we get it from df3 by joining on WarID

result = pd.merge(result, df3[['WarID', 'IsInternational']], on='WarID', how='left')

# Fill missing IsIntervention and IsInternational with 0 as per instructions
result['IsIntervention'] = result['IsIntervention'].fillna(0).astype(int)
result['IsInternational'] = result['IsInternational'].fillna(0).astype(int)

# Cast other columns to int as target schema requires
result['WarID'] = result['WarID'].astype(int)
result['WarShortName'] = result['WarShortName'].astype(str)
# WarShortName in target schema is integer, but source is string, so convert string to integer by length or hash?
# Target examples show WarShortName as integer equal to WarID, so convert WarShortName to WarID integer for consistency
# But that would lose info. Instead, convert WarShortName to integer by mapping unique strings to unique integers

warshortname_map = {v: k for k, v in enumerate(result['WarShortName'].unique(), start=1)}
result['WarShortName'] = result['WarShortName'].map(warshortname_map).astype(int)

result['WarType'] = result['WarType'].astype(int)

result = result[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)