import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_0.csv", index_col=0)

# Compute weighted average of Median weighted by Total per Major_category
grouped = df0.groupby("Major_category", as_index=False).apply(
    lambda x: pd.Series({
        "Median": (x["Median"] * x["Total"]).sum() / x["Total"].sum()
    })
)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts.csv", index=False)