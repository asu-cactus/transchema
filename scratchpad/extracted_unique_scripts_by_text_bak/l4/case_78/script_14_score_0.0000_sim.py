import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

join_0_2 = pd.merge(df0, df2, left_on="school", right_on="school", how="inner")

joined = pd.merge(join_0_2, df1, left_on="school", right_on="name", how="inner")

grouped = joined.groupby(["School ID", "name", "type", "size", "budget"], as_index=False).agg({
    "Average Math Score": "mean",
    "Average Reading Score": "mean",
    "Number Passing Math": "sum",
    "Number Passing Reading": "sum",
    "size": "max"
})

grouped = grouped.rename(columns={"size": "School Size"})

grouped = grouped.astype({
    "School ID": "int64",
    "name": "string",
    "type": "string",
    "size": "int64",
    "budget": "int64",
    "Average Math Score": "float64",
    "Average Reading Score": "float64",
    "Number Passing Math": "int64",
    "Number Passing Reading": "int64",
    "School Size": "int64"
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)