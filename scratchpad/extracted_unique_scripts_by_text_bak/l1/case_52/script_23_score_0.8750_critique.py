import pandas as pd
import glob

file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_52/training_*.csv")

dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

df_union = pd.concat(dfs, ignore_index=True)

result = df_union.groupby("condition", as_index=False)["click"].sum()

result.rename(columns={"click": "0"}, inplace=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)