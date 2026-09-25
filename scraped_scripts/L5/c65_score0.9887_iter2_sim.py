import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)

join_0 = pd.merge(source0, source4, left_on="Ord_id", right_on="Ord_id", how="inner")
join_1 = pd.merge(join_0, source1, left_on="Ship_id", right_on="Ship_id", how="inner")
join_2 = pd.merge(join_1, source2, left_on="Cust_id", right_on="Cust_id", how="inner")
join_3 = pd.merge(join_2, source3, left_on="Prod_id", right_on="Prod_id", how="inner")

grouped = join_3.groupby(["Prod_id", "Order_Priority"], as_index=False).agg(
    Ord_id=("Ord_id", "count"),
    Ship_id=("Ship_id", "count"),
    Cust_id=("Cust_id", "count"),
    Sales=("Sales", "sum"),
    Discount=("Discount", "sum"),
)

grouped["Ord_id"] = grouped["Ord_id"].astype(int)
grouped["Ship_id"] = grouped["Ship_id"].astype(int)
grouped["Cust_id"] = grouped["Cust_id"].astype(int)
grouped["Sales"] = grouped["Sales"].round().astype(int)
grouped["Discount"] = grouped["Discount"].round().astype(int)

result = grouped[["Prod_id", "Order_Priority", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)