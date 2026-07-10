import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_9.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df_pivot = df.groupby('year').size().reset_index(name='0')
df_pivot['year'] = df_pivot['year'].astype(int)
df_pivot['0'] = df_pivot['0'].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)