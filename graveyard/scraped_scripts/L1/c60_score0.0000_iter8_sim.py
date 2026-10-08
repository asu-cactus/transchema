import pandas as pd

paths = [f"autopipeline-benchmarks/github-pipelines/length1_60/training_{i}.csv" for i in range(60)]
dfs = [pd.read_csv(path, index_col=0) for path in paths]
df_all = pd.concat(dfs, ignore_index=True)
result = df_all.groupby('type', as_index=False)['driver_count'].sum()
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)