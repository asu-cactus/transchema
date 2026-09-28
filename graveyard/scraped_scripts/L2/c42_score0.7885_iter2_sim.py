import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_1.csv", index_col=0)

agg = df2.groupby("StoreType").agg(Store_count=("Store", "count"), Store_nunique=("Store", "nunique")).reset_index()

# The target schema is ['StoreType': string, 'Store': integer]
# The target examples show 'Store' as an integer count, presumably the count of stores per StoreType.
# Use the count of Store as 'Store' in the target.
result = agg[["StoreType", "Store_count"]].rename(columns={"Store_count": "Store"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_42/target_multisource_mcts.csv", index=False)