import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

s1_renamed = s1.rename(columns={"Order_Date": "Ship_Date"})
union_result = pd.concat([s1_renamed[["Ship_Date", "Ord_id"]], s4[["Ord_id", "Prod_id", "Ship_id"]].assign(Ship_Date=pd.NA)], ignore_index=True, sort=False)
# Fix union_result Ship_Date: s4 rows have NaN Ship_Date, so fill from s4 Ship_id by joining s0 to get Ship_Date
# But s4 rows have no Ship_Date, so we keep NaN for those rows for now

# Actually, better to union s1 and s4 on common columns only: Ord_id, Prod_id, Ship_id, Ship_Date
# s1 has no Prod_id or Ship_id, s4 has no Ship_Date filled
# So union only on columns present in both: Ord_id only? No, better to union s1 and s4 on Ord_id and Prod_id, Ship_id with NaNs where missing

# Instead, union s1 and s4 on columns: Ship_Date, Ord_id, Prod_id, Ship_id
# For s1, Prod_id and Ship_id missing -> NaN
# For s4, Ship_Date missing -> NaN

s1_exp = s1_renamed.copy()
s1_exp["Prod_id"] = pd.NA
s1_exp["Ship_id"] = pd.NA
s1_exp = s1_exp[["Ship_Date", "Ord_id", "Prod_id", "Ship_id"]]

s4_exp = s4.copy()
s4_exp["Ship_Date"] = pd.NA
s4_exp = s4_exp[["Ship_Date", "Ord_id", "Prod_id", "Ship_id"]]

union_result = pd.concat([s1_exp, s4_exp], ignore_index=True, sort=False)

joined_0 = union_result.merge(s0[["Ship_Date", "Ship_id"]], on="Ship_id", how="left", suffixes=("", "_s0"))
# Fill Ship_Date from s0 where missing in union_result
joined_0["Ship_Date"] = joined_0["Ship_Date"].combine_first(joined_0["Ship_Date_s0"])
joined_0 = joined_0.drop(columns=["Ship_Date_s0"])

joined_1 = joined_0.merge(s2[["Prod_id"]], on="Prod_id", how="left")

result = joined_1[["Ship_Date", "Ord_id", "Prod_id", "Ship_id"]]

result["Ship_Date"] = result["Ship_Date"].astype("string")
result["Ord_id"] = result["Ord_id"].str.extract(r'(\d+)').astype("Int64")
result["Prod_id"] = result["Prod_id"].str.extract(r'(\d+)').astype("Int64")
result["Ship_id"] = result["Ship_id"].str.extract(r'(\d+)').astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)