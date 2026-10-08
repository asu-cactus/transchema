import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_67/training_3.csv", index_col=0)

join_23 = pd.merge(s2, s3, on="Wrestler", suffixes=('_2015', '_2016'))

union_01 = pd.concat([s0, s1], ignore_index=True)

full_join = pd.merge(union_01, join_23, on="Wrestler", how="inner")

df = full_join.copy()

df_2013 = df[['Wrestler', 'Wins', 'Losses', 'Draws']].copy()
df_2013.columns = ['Wrestler', '2013 Wins', '2013 Losses', '2013 Draws']

df_2014 = df[['Wrestler', 'Wins_2015', 'Losses_2015', 'Draws_2015']].copy()
df_2014.columns = ['Wrestler', '2014 Wins', '2014 Losses', '2014 Draws']

df_2015 = df[['Wrestler', 'Wins_2016', 'Losses_2016', 'Draws_2016']].copy()
df_2015.columns = ['Wrestler', '2015 Wins', '2015 Losses', '2015 Draws']

df_2016 = s3[['Wrestler', 'Wins', 'Losses', 'Draws']].copy()
df_2016.columns = ['Wrestler', '2016 Wins', '2016 Losses', '2016 Draws']

merged = pd.merge(df_2013, df_2014, on='Wrestler', how='outer')
merged = pd.merge(merged, df_2015, on='Wrestler', how='outer')
merged = pd.merge(merged, df_2016, on='Wrestler', how='outer')

merged = merged.fillna(0)
int_cols = merged.columns.drop('Wrestler')
merged[int_cols] = merged[int_cols].astype(int)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_67/target_multisource_mcts.csv", index=False)