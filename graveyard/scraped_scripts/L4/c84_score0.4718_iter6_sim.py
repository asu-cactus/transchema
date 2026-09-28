import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

dfs = [s0, s1, s2, s3, s4]

for i, df in enumerate(dfs):
    df.columns = [col if col == 'age_grp' else f"{col}_{i}" for col in df.columns]

merged = dfs[0]
for i in range(1, len(dfs)):
    merged = merged.merge(dfs[i], on='age_grp', how='outer')

value_vars_count = [f"Count_{i}" for i in range(len(dfs))]
value_vars_notes = [f"Notes_{i}" for i in range(len(dfs))]
value_vars_rate = [f"Rate_{i}" for i in range(len(dfs))]
value_vars_stats = [f"Statistics_{i}" for i in range(len(dfs))]

count_melt = merged.melt(id_vars=['age_grp'], value_vars=value_vars_count, var_name='source', value_name='Count')
notes_melt = merged.melt(id_vars=['age_grp'], value_vars=value_vars_notes, var_name='source', value_name='Notes')
rate_melt = merged.melt(id_vars=['age_grp'], value_vars=value_vars_rate, var_name='source', value_name='Rate')
stats_melt = merged.melt(id_vars=['age_grp'], value_vars=value_vars_stats, var_name='source', value_name='Statistics')

df_all = count_melt[['age_grp', 'Count', 'source']].merge(
    notes_melt[['age_grp', 'Notes', 'source']], on=['age_grp', 'source'], how='outer').merge(
    rate_melt[['age_grp', 'Rate', 'source']], on=['age_grp', 'source'], how='outer').merge(
    stats_melt[['age_grp', 'Statistics', 'source']], on=['age_grp', 'source'], how='outer')

df_all = df_all.drop(columns=['source'])

df_all = df_all[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)