import pandas as pd

src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)

union_df = pd.concat([src3, src4, src5, src7], ignore_index=True)

result = pd.DataFrame()
result['ARPU'] = [union_df['ARPU'].mean()]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)