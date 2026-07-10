import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
result = df0.groupby("J_CALL", as_index=False).size().drop(columns="size")
result.columns = ["V_GENE"]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)