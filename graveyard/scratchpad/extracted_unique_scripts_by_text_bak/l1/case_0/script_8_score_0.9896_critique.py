import pandas as pd
import glob

file_pattern = "autopipeline-benchmarks/github-pipelines/length1_0/training_*.csv"
files = glob.glob(file_pattern)

dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("State", as_index=False)["AverageTemperature"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)