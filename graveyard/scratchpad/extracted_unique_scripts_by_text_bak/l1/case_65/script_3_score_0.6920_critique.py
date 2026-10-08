import pandas as pd
import glob

file_paths = sorted(glob.glob("autopipeline-benchmarks/github-pipelines/length1_65/training_*.csv"))
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(dfs, ignore_index=True)
result = df_all.groupby("year").size().reset_index(name="0")
result["year"] = result["year"].astype(int)
result["0"] = result["0"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)