import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
result = df_union.groupby("Gender", as_index=False).size()
result.columns = ["Gender", "0"]
result["0"] = result["0"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)