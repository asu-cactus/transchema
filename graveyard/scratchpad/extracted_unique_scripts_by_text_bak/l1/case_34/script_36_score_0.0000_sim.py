import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)
df = df.rename(columns={"J_CALL": "V_GENE"})
df = df.groupby("V_GENE", as_index=False).size().drop(columns="size", errors='ignore')
df = df[["V_GENE"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)