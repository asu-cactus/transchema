import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_4.csv", index_col=0)

join_0 = pd.merge(source4, source0, on="Prod_id", how="inner")
join_1 = pd.merge(join_0, source1, left_on="Ord_id", right_on="Ord_id", how="inner")
join_2 = pd.merge(join_1, source3, left_on="Ship_id", right_on="Ship_id", how="inner")
join_3 = pd.merge(join_2, source2, left_on="Cust_id", right_on="Cust_id", how="inner")

result = join_3.groupby("Sales", as_index=False).size()
# The groupby on Sales with size() returns counts, but target schema expects Sales as float sums or just Sales column.
# The partial plan says GROUP_BY : [Sales], but Sales is float and target schema is just Sales: float.
# So likely the intention is to aggregate Sales by summing or just get unique Sales values.
# Since Sales is float and target examples show float values, we should sum Sales grouped by no key (total sum),
# but partial plan says GROUP_BY : [Sales], which is unusual.
# Instead, we interpret the plan as grouping by Sales to get unique Sales values (like distinct Sales).
# But target examples show multiple Sales values, so we just select Sales column distinct values.

# To match target schema ['Sales': float], we just select Sales column and drop duplicates.
final = join_3[["Sales"]].drop_duplicates().reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_81/target_multisource_mcts.csv", index=False)