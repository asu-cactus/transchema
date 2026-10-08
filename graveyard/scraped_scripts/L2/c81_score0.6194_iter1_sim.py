import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)

df_union = pd.concat([df1, df2], ignore_index=True)
df_result = df_union[['city', 'driver_count']].copy()
df_result['driver_count'] = df_result['driver_count'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_81/target_multisource_mcts.csv", index=False)