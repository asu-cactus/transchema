import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

j03 = pd.merge(s3, s0, on="WarID", how="inner", suffixes=('_3', '_0'))
j031 = pd.merge(j03, s1, on="WarID", how="inner", suffixes=('', '_1'))
j0312 = pd.merge(j031, s2, on="WarID", how="inner", suffixes=('', '_2'))

grp = j0312.groupby(
    ['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational'],
    as_index=False
).size()

result = grp.rename(columns={'size': 'Count'})  # size() returns a Series, so fix below

# Because groupby.size() returns a Series, redo groupby with agg to keep columns
result = j0312.groupby(
    ['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational'],
    as_index=False
).agg({'WarID':'count'})

# The count column is not needed, just keep the grouping columns
result = result[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)