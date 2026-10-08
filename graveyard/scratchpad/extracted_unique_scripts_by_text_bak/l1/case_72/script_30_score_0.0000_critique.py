import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

result = df.groupby('condition', as_index=False).agg({'click': 'count'})
result = result.rename(columns={'click': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)