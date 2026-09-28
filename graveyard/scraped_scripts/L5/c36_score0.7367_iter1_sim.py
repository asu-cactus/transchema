import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_36/training_0.csv", index_col=0)

cases = df.filter(regex="^Cases_").copy()
deaths = df.filter(regex="^Deaths_").copy()

cases.columns = cases.columns.str.replace("Cases_", "")
deaths.columns = deaths.columns.str.replace("Deaths_", "")

cases_long = cases.melt(var_name="Country", value_name="Count")
cases_long["variable"] = "Cases"
deaths_long = deaths.melt(var_name="Country", value_name="Count")
deaths_long["variable"] = "Deaths"

combined = pd.concat([cases_long, deaths_long], ignore_index=True)
combined = combined.dropna(subset=["Count"])

combined["variable"] = combined["variable"] + ", " + combined["Country"]
result = combined[["variable"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_36/target_multisource_mcts.csv", index=False)