import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_90/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

result = pd.DataFrame({'occluded': [df_all['occluded'].sum()]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_90/target_multisource_mcts.csv", index=False)