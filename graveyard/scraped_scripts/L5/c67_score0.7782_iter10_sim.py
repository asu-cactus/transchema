import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

df_2_1 = pd.merge(source2, source1, on="Ship_id", how="inner")

df_2_1_4 = pd.merge(df_2_1, source4, on="Ord_id", how="inner")

result = df_2_1_4[["Ship_Date", "Prod_id", "Ord_id", "Ship_id", "Cust_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)