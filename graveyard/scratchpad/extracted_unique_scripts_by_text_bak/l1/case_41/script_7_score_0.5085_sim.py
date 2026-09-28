import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on=["zipcode", "AGI_STUB"], suffixes=('_left', '_right'))

grouped = joined.groupby(["zipcode", "AGI_STUB"], as_index=False).agg({
    "N1_left": "sum",
    "A00100_left": "sum"
})

result = grouped.rename(columns={
    "N1_left": "N1",
    "A00100_left": "A00100"
})

result = result.astype({
    "zipcode": "int64",
    "AGI_STUB": "int64",
    "N1": "int64",
    "A00100": "int64"
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)