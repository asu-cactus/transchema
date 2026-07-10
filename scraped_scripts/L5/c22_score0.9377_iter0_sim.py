import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_22/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_22/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length5_22/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df1.groupby("school_name", as_index=False)["math_score"].sum()
grouped["math_score"] = grouped["math_score"].astype(int)

grouped.to_csv(target_path, index=False)