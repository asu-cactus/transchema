import pandas as pd

Source4_78_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
Source4_78_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
Source4_78_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

join_result_1 = pd.merge(Source4_78_0, Source4_78_1, left_on="school", right_on="name", how="inner")

join_result_2 = pd.merge(join_result_1, Source4_78_2, left_on="name", right_on="school", how="inner")

agg = join_result_2.groupby(
    ["name", "School ID", "type", "size", "budget"],
    as_index=False
).agg(
    **{
        "Average Math Score": ("math_score", "mean"),
        "Average Reading Score": ("reading_score", "mean"),
        "Number Passing Math": (lambda df: (df["math_score"] >= 70).sum()),
        "Number Passing Reading": (lambda df: (df["reading_score"] >= 70).sum()),
        "School Size": ("size", "max"),
    }
)

agg = agg[[
    "School ID",
    "name",
    "type",
    "size",
    "budget",
    "Average Math Score",
    "Average Reading Score",
    "Number Passing Math",
    "Number Passing Reading",
    "School Size"
]]

agg = agg.rename(columns={"size": "size"})  # keep 'size' as is (target schema has 'size')

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)