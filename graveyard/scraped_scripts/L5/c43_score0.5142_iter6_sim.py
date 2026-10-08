import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

joined_4_2 = pd.merge(source4, source2, on="Ship_id", how="inner")
joined_4_2_0 = pd.merge(joined_4_2, source0, on="Ord_id", how="inner")
joined_4_2_0_1 = pd.merge(joined_4_2_0, source1, on="Cust_id", how="inner")
final_join = pd.merge(joined_4_2_0_1, source3, on="Prod_id", how="inner")

result = final_join[["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]].copy()

result["Ord_id"] = result["Ord_id"].apply(lambda x: int(x.split("_")[1]) if isinstance(x, str) and "_" in x else pd.NA)
result["Prod_id"] = result["Prod_id"].apply(lambda x: int(x.split("_")[1]) if isinstance(x, str) and "_" in x else pd.NA)
result["Ship_id"] = result["Ship_id"].apply(lambda x: int(x.split("_")[1]) if isinstance(x, str) and "_" in x else pd.NA)
result["Cust_id"] = result["Cust_id"].apply(lambda x: int(x.split("_")[1]) if isinstance(x, str) and "_" in x else pd.NA)
result["Sales"] = result["Sales"].round(0).astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)