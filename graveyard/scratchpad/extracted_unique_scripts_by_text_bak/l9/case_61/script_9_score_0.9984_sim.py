import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby("start", as_index=False).agg(
    betterliving_count=pd.NamedAgg(column="betterliving", aggfunc="count"),
    betterliving_sum=pd.NamedAgg(column="betterliving", aggfunc="sum")
)

# According to the partial plan, the target schema is ['start', 'betterliving'] with betterliving as integer.
# The example shows betterliving as 1 for each start date, so likely the count or sum is 1 per start.
# The partial plan shows COUNT and SUM but target schema has only one betterliving column.
# We choose SUM(betterliving) as the final betterliving column because betterliving values are 1 in sources.
# Drop the count column and rename sum column to betterliving.

result = agg[["start", "betterliving_sum"]].rename(columns={"betterliving_sum": "betterliving"})
result["betterliving"] = result["betterliving"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_61/target_multisource_mcts.csv", index=False)