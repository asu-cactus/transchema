import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_1.csv", index_col=0)

pivot_df = df0.pivot_table(index='fname', columns='ok_row_num', values='ok_col_num', aggfunc='count', fill_value=0)
pivot_df['row_count'] = pivot_df.sum(axis=1)
result = pivot_df[['row_count']].reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_49/target_multisource_mcts.csv", index=False)