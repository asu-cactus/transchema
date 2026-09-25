import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_1.csv", index_col=0)

agg_0 = df0.groupby(['state', 'date'], as_index=False)['draw_sales'].sum()
agg_1 = df1.groupby(['state', 'date'], as_index=False)['draw_sales'].sum()

union = pd.concat([agg_0, agg_1], ignore_index=True)

agg_union = union.groupby(['state', 'date'], as_index=False)['draw_sales'].sum()

agg_union['year'] = agg_union['date'].str[:4].astype(int)

agg_union.to_csv("autopipeline-benchmarks/github-pipelines/length2_21/target_multisource_mcts.csv", index=False)