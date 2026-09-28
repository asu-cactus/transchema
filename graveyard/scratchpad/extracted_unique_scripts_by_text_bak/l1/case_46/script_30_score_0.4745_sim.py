import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

df_result = df.rename(columns={"Text Date": "Date", "Water Use": "Water Use", "Power Use": "Power Use"})
df_result = df_result[["Date", "Water Use", "Power Use"]]
df_result["Water Use"] = df_result["Water Use"].astype(float)
df_result["Power Use"] = df_result["Power Use"].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)