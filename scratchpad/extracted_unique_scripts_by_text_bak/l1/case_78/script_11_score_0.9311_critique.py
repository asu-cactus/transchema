import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

# Group by Product and aggregate Price by mean
df_result = df0.groupby("Product", as_index=False).agg({"Price": "mean"})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)