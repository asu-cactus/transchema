import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, left_on="Source Zipcode", right_on="Source Zipcode", suffixes=('', '_dup'))

result = joined.groupby("Source Zipcode", as_index=False)["Counts"].sum()

result = result.rename(columns={"Source Zipcode": "Source Zipcode", "Counts": "Counts"})

result["Source Zipcode"] = result["Source Zipcode"].astype(int)
result["Counts"] = result["Counts"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)