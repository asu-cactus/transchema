import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

agg_df = df0.groupby(["zipcode", "AGI_STUB"], as_index=False).agg({
    "N1": "sum",
    "A00100": "sum"
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)