import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)

r0 = pd.merge(src2, src1, on="Ship_id", how="inner")
r1 = pd.merge(r0, src0, on="Cust_id", how="inner")
r2 = pd.merge(r1, src3, on="Ord_id", how="inner")

out = pd.DataFrame()
out["Ship_Date"] = r2["Ship_Date"].astype(str)
out["Customer_Name"] = r2["Customer_Name"].astype(str)
out["Ord_id"] = r2["Ord_id"].str.replace("Ord_", "").astype(int)
out["Prod_id"] = r2["Prod_id"].str.replace("Prod_", "").astype(int)
out["Ship_id"] = r2["Ship_id"].str.replace("SHP_", "").astype(int)

out.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)