import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_0.csv", index_col=0)

agg = df0.groupby('fname').agg({'ok_col_num':'sum', 'ok_row_num':'sum'}).reset_index()
agg['row_count'] = agg['ok_col_num'] + agg['ok_row_num']
result = agg[['fname', 'row_count']]
result['row_count'] = result['row_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_49/target_multisource_mcts.csv", index=False)