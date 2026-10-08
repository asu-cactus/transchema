import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Filter rows where 'Statistics' is not null (to match target examples)
df_all = df_all[df_all['Statistics'].notna()]

# Group by 'age_grp' and 'Statistics'
agg = df_all.groupby(['age_grp', 'Statistics'], dropna=False).agg(
    Count=('Count', 'sum'),
    Rate=('Rate', 'mean'),
    Notes=pd.NamedAgg(column='Notes', aggfunc=lambda x: pd.NA)  # Notes is NaN in target
).reset_index()

# Reorder columns to match target schema
agg = agg[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)