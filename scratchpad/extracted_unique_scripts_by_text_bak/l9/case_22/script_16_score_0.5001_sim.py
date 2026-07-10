import pandas as pd

src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)

union_df = pd.concat([src3, src4, src7, src8], ignore_index=True)

merged = pd.merge(union_df[['ROW_WID']], src1[['ROW_WID', 'INBOUND_CALLS_NUM']], on='ROW_WID', how='inner')

result = pd.DataFrame({'INBOUND_CALLS_NUM': [merged['INBOUND_CALLS_NUM'].sum()]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)