import pandas as pd

source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_2.csv"
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("fac_type", as_index=False)["capacity"].sum()
result["capacity"] = result["capacity"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)