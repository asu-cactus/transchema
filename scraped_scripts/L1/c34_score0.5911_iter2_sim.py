import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
result = df0.groupby("J_CALL").size().reset_index(name="count")
result = result.rename(columns={"J_CALL": "V_GENE"})
result[["V_GENE"]].to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)