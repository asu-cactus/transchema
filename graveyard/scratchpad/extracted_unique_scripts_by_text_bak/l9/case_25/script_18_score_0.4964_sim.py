import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)

df_union = pd.concat([df0, df1, df4, df5], ignore_index=True)
result = df_union[['CANCEL_DT']].copy()
result['CANCEL_DT'] = result['CANCEL_DT'].astype(str).replace('nan', pd.NA)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)