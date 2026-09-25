import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

union_0 = pd.concat([src0, src1, src8, src9], ignore_index=True)

joined = pd.merge(union_0[['ROW_WID']], src4[['ROW_WID', 'TECHSUPPORT_NUM']], on='ROW_WID', how='inner')

result = joined[['TECHSUPPORT_NUM']].copy()
result['TECHSUPPORT_NUM'] = result['TECHSUPPORT_NUM'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)