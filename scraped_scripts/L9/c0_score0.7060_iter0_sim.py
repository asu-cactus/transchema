import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_0/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('0', as_index=False).size()
result.columns = ['0', 'count']

final = result[['0', 'count']].rename(columns={'count': '0'})
final['0'] = final['0'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_0/target_multisource_mcts.csv", index=False)