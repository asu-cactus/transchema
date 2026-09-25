import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

agg_df = df0.groupby("zipcode", as_index=False).agg({
    "AGI_STUB": "sum",
    "N1": "sum",
    "A00100": "sum"
})

agg_df = agg_df.astype({
    "zipcode": "int64",
    "AGI_STUB": "int64",
    "N1": "int64",
    "A00100": "int64"
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)