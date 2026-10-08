import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

df_unpivot = df0.melt(
    id_vars=['PRECINCT', 'ELIGIBLE_VOTERS', 'POLLS', 'EARLY_VOING', 'ABSENTEE', 'PROVISIONAL'],
    value_vars=[],
    var_name='variable',
    value_name='value'
)

# Since partial plan says UNPIVOT then PIVOT, but source already has columns matching target except PARTY and district columns,
# and target does not have PARTY or district columns, we can aggregate by PRECINCT summing numeric columns.

df_agg = df0.groupby('PRECINCT', as_index=False).agg({
    'ELIGIBLE_VOTERS': 'sum',
    'POLLS': 'sum',
    'EARLY_VOING': 'sum',
    'ABSENTEE': 'sum',
    'PROVISIONAL': 'sum'
})

df_agg['PRECINCT'] = df_agg['PRECINCT'].astype(str)
df_agg['ELIGIBLE_VOTERS'] = df_agg['ELIGIBLE_VOTERS'].astype(int)
df_agg['POLLS'] = df_agg['POLLS'].astype(int)
df_agg['EARLY_VOING'] = df_agg['EARLY_VOING'].astype(int)
df_agg['ABSENTEE'] = df_agg['ABSENTEE'].astype(int)
df_agg['PROVISIONAL'] = df_agg['PROVISIONAL'].astype(int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)