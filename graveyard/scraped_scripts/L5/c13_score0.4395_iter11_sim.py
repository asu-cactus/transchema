import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

agg = s1.merge(s3, on="Prod_id", how="inner")
grouped = agg.groupby("Product_Sub_Category").agg(
    Ord_id_count=pd.NamedAgg(column="Ord_id", aggfunc="count"),
    Prod_id_count_distinct=pd.NamedAgg(column="Prod_id", aggfunc=pd.Series.nunique),
    Sales_sum=pd.NamedAgg(column="Sales", aggfunc="sum"),
    Discount_avg=pd.NamedAgg(column="Discount", aggfunc="mean"),
).reset_index()

joined_1 = pd.merge(grouped, s3, left_on="Product_Sub_Category", right_on="Product_Sub_Category", how="inner")
joined_2 = pd.merge(joined_1, s1, on=["Prod_id"], how="inner")
joined_3 = pd.merge(joined_2, s0, on="Ord_id", how="inner")
joined_4 = pd.merge(joined_3, s2, on="Cust_id", how="inner")
final_join = pd.merge(joined_4, s4, on="Ship_id", how="inner")

result = final_join[["Product_Sub_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()

result["Ord_id"] = result["Ord_id"].str.extract(r'(\d+)').astype(int)
result["Prod_id"] = result["Prod_id"].str.extract(r'(\d+)').astype(int)
result["Ship_id"] = result["Ship_id"].str.extract(r'(\d+)').astype(int)
result["Cust_id"] = result["Cust_id"].str.extract(r'(\d+)').astype(int)
result["Sales"] = result["Sales"].round().astype(int)
result["Discount"] = (result["Discount"] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)