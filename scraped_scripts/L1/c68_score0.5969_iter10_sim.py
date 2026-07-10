import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_68/training_0.csv", index_col=0)
df_grouped = df0.groupby("V_CALL").size().reset_index(name="count")
df_grouped["V_GENE"] = df_grouped["V_CALL"].str.split("-", n=1).str[0]
result = df_grouped[["V_GENE"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_68/target_multisource_mcts.csv", index=False)