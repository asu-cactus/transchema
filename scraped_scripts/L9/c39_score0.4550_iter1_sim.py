import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_39/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_10.csv",
]

pivoted_dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    df = df.reset_index().rename(columns={'index': 'idx'})
    df['source'] = i
    pivot = df.pivot(index='idx', columns='source', values='0')
    pivoted_dfs.append(pivot)

result = pd.concat(pivoted_dfs, axis=1)
result = result.fillna(0).astype(int)
final = pd.DataFrame(result.sum(axis=1), columns=['0'])
final.to_csv("autopipeline-benchmarks/github-pipelines/length9_39/target_multisource_mcts.csv")