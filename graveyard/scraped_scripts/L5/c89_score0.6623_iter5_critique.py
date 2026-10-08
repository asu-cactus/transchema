import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

merged = df4.merge(df0, on="Prod_id", how="inner") \
            .merge(df1, on="Cust_id", how="inner") \
            .merge(df2, on="Ord_id", how="inner") \
            .merge(df3, on="Ship_id", how="inner")

result = merged.groupby("Customer_Segment", as_index=False).agg({"Profit": "sum"})[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)