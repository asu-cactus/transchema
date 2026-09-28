import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

joined = pd.merge(df, df, on="year", suffixes=('_left', '_right'))

unpivoted = joined.melt(id_vars=["year"], value_vars=["year"], var_name="variable", value_name="0")

result = unpivoted[["year", "0"]].copy()
result["0"] = pd.to_numeric(result["0"], errors='coerce').fillna(0).astype(int)
result["year"] = pd.to_numeric(result["year"], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)