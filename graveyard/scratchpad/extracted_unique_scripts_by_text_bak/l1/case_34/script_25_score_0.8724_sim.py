import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
union_result = pd.concat([df1, df2], ignore_index=True)
union_result = union_result.rename(columns={"J_CALL": "V_GENE"})
union_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)