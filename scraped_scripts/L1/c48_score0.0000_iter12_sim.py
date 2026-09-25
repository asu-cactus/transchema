import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_48/training_9.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_out = pd.DataFrame()
df_out['Date'] = df_all['Text Date'].astype(str)
df_out['Water Use'] = df_all['Water Use'].astype(float)
df_out['Power Use'] = df_all['Power Use'].astype(int)

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)