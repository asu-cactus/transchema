import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

join_1 = pd.merge(s4, s3, on="Ship_id", how="inner")
join_2 = pd.merge(join_1, s0, on="Ord_id", how="inner")
join_3 = pd.merge(join_2, s1, on="Cust_id", how="inner")
join_4 = pd.merge(join_3, s2, on="Prod_id", how="inner")

result = join_4[["Prod_id", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()

result["Ord_id"] = result["Ord_id"].apply(lambda x: int(x.split("_")[1]) if isinstance(x, str) and "_" in x else pd.NA)
result["Ship_id"] = result["Ship_id"].apply(lambda x: int(x.split("_")[1]) if isinstance(x, str) and "_" in x else pd.NA)
result["Cust_id"] = result["Cust_id"].apply(lambda x: int(x.split("_")[1]) if isinstance(x, str) and "_" in x else pd.NA)
result["Sales"] = result["Sales"].round().astype("Int64")
result["Discount"] = (result["Discount"] * 100).round().astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)