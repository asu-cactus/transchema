import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)

grouped = df0.groupby(['sex', 'smoker'], as_index=False).agg({'tip':'sum', 'total_bill':'sum'})

grouped['tip_pct'] = grouped['tip'] / grouped['total_bill']

result = grouped[['sex', 'smoker', 'tip_pct']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)