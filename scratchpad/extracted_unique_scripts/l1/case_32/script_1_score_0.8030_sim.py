import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, how="inner", on="school_name")

merged = merged.rename(columns={"School ID": "School ID", "type": "type", "size": "size", "budget": "budget"})

merged = merged[[
    "Student ID",
    "student_name",
    "gender",
    "grade",
    "school_name",
    "reading_score",
    "math_score",
    "School ID",
    "type",
    "size",
    "budget"
]]

merged["Student ID"] = merged["Student ID"].astype(int)
merged["reading_score"] = merged["reading_score"].astype(int)
merged["math_score"] = merged["math_score"].astype(int)
merged["School ID"] = merged["School ID"].astype(int)
merged["size"] = merged["size"].astype(int)
merged["budget"] = merged["budget"].astype(int)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_32/target_multisource_mcts.csv", index=False)