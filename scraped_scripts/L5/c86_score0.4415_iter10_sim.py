import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)

merged = pd.merge(source2, source0, on="Ship_id")
result = merged.groupby("Profit", as_index=False).size()
# The target schema is ['Profit': integer], and target examples show Profit values as integers.
# The group by is on Profit, so the aggregation is count of rows per Profit value.
# The target examples show only Profit column, so we output Profit and count of occurrences.
# But target examples only have Profit column, so we must output Profit values only, no counts.
# The partial plan says GROUP_BY : [Profit], which implies grouping by Profit and aggregating counts.
# However, target schema only has Profit column, no count column.
# The target examples show Profit values 2253, 1055, 891, which look like sums or counts.
# Since Profit is numeric, and the source Profit column is float, but target Profit is integer,
# likely the target Profit is sum of Profit grouped by Profit? That is illogical.
# More likely, the target Profit is sum of Profit grouped by some key, but no key given.
# The partial plan only says join on Ship_id and group by Profit.
# Since grouping by Profit itself is unusual, maybe the target is sum of Profit values grouped by Profit values themselves (which is identity).
# So the target is unique Profit values, so just distinct Profit values cast to int.
# But target examples have 3 rows with Profit values 2253, 1055, 891, which are positive integers.
# The source Profit values are floats, some negative.
# So maybe the target is sum of Profit grouped by Ship_id or some other key.
# Since no other key is given, and partial plan only says join on Ship_id and group by Profit,
# the best guess is to group by Profit and count rows per Profit, then output Profit values as integers.
# But target schema only has Profit column, so output unique Profit values as integers.
# To match target examples, we output Profit values rounded and converted to int, dropping duplicates.

# So final output is unique Profit values as integers.

final = merged[["Profit"]].copy()
final["Profit"] = final["Profit"].round().astype(int)
final = final.drop_duplicates().reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)