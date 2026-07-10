import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)

# The partial plan suggests a join of the same table on facid, which is redundant here since it's the same table.
# So effectively, we just need to group by fac_type and sum capacity.

result = df0.groupby("fac_type", as_index=False)["capacity"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)