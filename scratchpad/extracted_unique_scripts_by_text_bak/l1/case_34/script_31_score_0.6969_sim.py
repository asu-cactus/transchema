import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
df0 = df0.rename(columns={"J_CALL": "V_GENE"})
result = df0.groupby("V_GENE", as_index=False).size().drop(columns=["size"])
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)