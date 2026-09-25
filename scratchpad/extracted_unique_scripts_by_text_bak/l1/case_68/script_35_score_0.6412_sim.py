import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
result = df.groupby("V_CALL", as_index=False).size().rename(columns={"V_CALL": "V_GENE", "size": "count"})
result = result[["V_GENE"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)