import pandas as pd

# Read all source tables - here only one source table is given, but if more exist, read them similarly and union
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

# If there were multiple source tables, e.g. df1, df2, ..., we would do:
# df_all = pd.concat([df0, df1, df2, ...], ignore_index=True)
# Here only one source table is given, so df_all = df0
df_all = df0

# Group by PRECINCT and sum the numeric columns
df_agg = df_all.groupby('PRECINCT', as_index=False).agg({
    'ELIGIBLE_VOTERS': 'sum',
    'POLLS': 'sum',
    'EARLY_VOING': 'sum',
    'ABSENTEE': 'sum',
    'PROVISIONAL': 'sum'
})

# Cast columns to correct types as per target schema
df_agg['PRECINCT'] = df_agg['PRECINCT'].astype(str)
df_agg['ELIGIBLE_VOTERS'] = df_agg['ELIGIBLE_VOTERS'].astype(int)
df_agg['POLLS'] = df_agg['POLLS'].astype(int)
df_agg['EARLY_VOING'] = df_agg['EARLY_VOING'].astype(int)
df_agg['ABSENTEE'] = df_agg['ABSENTEE'].astype(int)
df_agg['PROVISIONAL'] = df_agg['PROVISIONAL'].astype(int)

# Write output
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)