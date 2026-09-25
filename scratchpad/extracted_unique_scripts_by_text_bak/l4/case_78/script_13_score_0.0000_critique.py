import pandas as pd

# Read sources
Source4_78_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
Source4_78_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
Source4_78_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

# Join Source4_78_1 (school dimension) with Source4_78_2 (student data) on school name
joined = pd.merge(Source4_78_1, Source4_78_2, left_on="name", right_on="school", how="inner")

# Group by the leftmost unique keys in target schema
agg = joined.groupby(
    ["School ID", "name", "type", "size", "budget"],
    as_index=False
).agg(
    Average_Math_Score = ("math_score", "mean"),
    Average_Reading_Score = ("reading_score", "mean"),
    Number_Passing_Math = (lambda df: (df["math_score"] >= 70).sum()),
    Number_Passing_Reading = (lambda df: (df["reading_score"] >= 70).sum()),
    School_Size = ("size", "max")
)

# Rename columns to match target schema exactly
agg = agg.rename(columns={
    "Average_Math_Score": "Average Math Score",
    "Average_Reading_Score": "Average Reading Score",
    "Number_Passing_Math": "Number Passing Math",
    "Number_Passing_Reading": "Number Passing Reading",
    "School_Size": "School Size"
})

# Reorder columns to match target schema
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

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)