import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="Major_category")

result = joined.groupby("Major_category", as_index=False).agg({"Median_x": "median"})

result = result.rename(columns={"Major_category": "Major_category", "Median_x": "Median"})

result["Median"] = result["Median"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts.csv", index=False)