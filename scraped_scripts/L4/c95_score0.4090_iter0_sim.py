import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_95/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

agg_df = df.groupby(['Subject', 'SubjectId', 'Split'], as_index=False).sum()

agg_df = agg_df[['Subject', 'SubjectId', 'Split', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

agg_df['SubjectId'] = agg_df['SubjectId'].astype(int)
agg_df['Split'] = agg_df['Split'].astype(str)
agg_df['Subject'] = agg_df['Subject'].astype(str)
agg_df[['PA','AB','H','TB','BB','SF','HBP']] = agg_df[['PA','AB','H','TB','BB','SF','HBP']].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_95/target_multisource_mcts.csv", index=False)