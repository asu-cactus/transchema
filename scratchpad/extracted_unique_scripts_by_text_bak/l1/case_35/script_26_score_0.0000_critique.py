import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df[['Source Zipcode', 'Counts']]

df['Source Zipcode'] = df['Source Zipcode'].astype(int)
df['Counts'] = df['Counts'].astype(int)

df = df.groupby('Source Zipcode', as_index=False).agg({'Counts': 'sum'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)