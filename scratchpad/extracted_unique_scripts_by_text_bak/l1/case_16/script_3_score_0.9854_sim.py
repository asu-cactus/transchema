import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df_grouped = df0.groupby("CUSTOMERNAME", as_index=False)["ORDERNUMBER"].count()
df_grouped = df_grouped.rename(columns={"ORDERNUMBER": "ORDERNUMBER"})
df_grouped["ORDERNUMBER"] = df_grouped["ORDERNUMBER"].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)