import pandas as pd

source1_path = "autopipeline-benchmarks/github-pipelines/length2_9/training_1.csv"

df1 = pd.read_csv(source1_path, index_col=0)
df_union = pd.concat([df1, df1], ignore_index=True)
result = df_union[['city', 'driver_count']].copy()
result['driver_count'] = result['driver_count'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_9/target_multisource_mcts.csv", index=False)