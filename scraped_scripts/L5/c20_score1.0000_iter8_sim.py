import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_4.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

agg_df = df_all.groupby('longitude').agg(
    missing_count=pd.NamedAgg(column='missing_count', aggfunc='sum'),
    state=pd.NamedAgg(column='state', aggfunc='count'),
    latitude=pd.NamedAgg(column='latitude', aggfunc='mean')
).reset_index()

agg_df['missing_count'] = agg_df['missing_count'].astype(int)
agg_df['state'] = agg_df['state'].astype(int)
agg_df['latitude'] = agg_df['latitude'].round().astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_20/target_multisource_mcts.csv", index=False)