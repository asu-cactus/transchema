import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_1.csv", index_col=0)

grouped = df1.groupby(['city']).agg({'fare':'mean'}).reset_index()

# Since target schema requires 'city', 'type', 'fare', and 'type' only exists in df0,
# join grouped fare with df0 on city, then keep city, type, fare columns.
joined = pd.merge(df0[['city','type']], grouped, on='city', how='inner')

joined = joined[['city','type','fare']]
joined.to_csv("autopipeline-benchmarks/github-pipelines/length3_76/target_multisource_mcts.csv", index=False)