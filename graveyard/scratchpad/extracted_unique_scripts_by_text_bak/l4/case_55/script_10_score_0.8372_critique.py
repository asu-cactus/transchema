import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# Define a mode aggregation function that returns the smallest mode if multiple modes exist
def mode_agg(series):
    modes = series.mode()
    if len(modes) == 0:
        return pd.NA
    else:
        return modes.min()

result = df_all.groupby("WarNum", as_index=False).agg({"WhereFought": mode_agg})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)