import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
result = union_df.rename(columns={"J_CALL": "V_GENE"})
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)