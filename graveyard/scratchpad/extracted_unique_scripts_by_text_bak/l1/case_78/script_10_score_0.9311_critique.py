import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

# Since only one source table is given, UNION is trivial
df_union = df0.copy()

# Group by Product and aggregate Price by mean
agg = df_union.groupby("Product", as_index=False)["Price"].mean()

agg.columns = ["Product", "Price"]
agg["Price"] = agg["Price"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)