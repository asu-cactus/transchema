import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

agg_df = df_all.groupby('hero', as_index=False).agg({
    'disadvantage': 'mean',
    'winrate': 'mean',
    'matches': 'sum'
})

agg_df['disadvantage'] = agg_df['disadvantage'].astype(float)
agg_df['winrate'] = agg_df['winrate'].astype(float)
agg_df['matches'] = agg_df['matches'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)