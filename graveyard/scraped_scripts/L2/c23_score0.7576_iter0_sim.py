import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

grouped = df0.groupby('city', as_index=False).agg({'ride_id':'count'}).rename(columns={'ride_id':'type'})

merged = pd.merge(grouped, df1[['city','type']], on='city', how='inner')

# Convert 'type' from df1 (string) to integer count from grouped
# The target schema 'type' is integer and from the example it matches the count from df0
# So we keep the count from grouped as 'type' and discard df1.type string column
result = merged[['city', 'type_x']].rename(columns={'type_x':'type'})

result['type'] = result['type'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)