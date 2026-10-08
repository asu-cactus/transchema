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
    "autopipeline-benchmarks/github-pipelines/length1_34/training_8.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    df = df.rename(columns={"J_CALL": "V_GENE"})
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)
result = union_df.groupby("V_GENE", as_index=False).size()
result = result.rename(columns={"size": "V_GENE"})
result = result[["V_GENE"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)