import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_36/training_0.csv", index_col=0)

cases_cols = [col for col in df.columns if col.startswith("Cases_")]
melted = df.melt(id_vars=["Date", "Day"], value_vars=cases_cols, var_name="variable", value_name="value")
melted = melted.dropna(subset=["value"])
melted["variable"] = melted["variable"].str.replace("Cases_", "Cases", regex=False)

result = melted.groupby("variable", as_index=False).size().rename(columns={"size": "count"})
result = result[["variable"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_36/target_multisource_mcts.csv", index=False)