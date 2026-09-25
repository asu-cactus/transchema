import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_27/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_27/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="school_name", how="inner")

merged = merged.rename(columns={
    "school_name": "school_name",
    "Student ID": "Student ID",
    "student_name": "student_name",
    "gender": "gender",
    "grade": "grade",
    "reading_score": "reading_score",
    "math_score": "math_score",
    "School ID": "School ID",
    "type": "type",
    "size": "size",
    "budget": "budget"
})

merged = merged[[
    "school_name",
    "Student ID",
    "student_name",
    "gender",
    "grade",
    "reading_score",
    "math_score",
    "School ID",
    "type",
    "size",
    "budget"
]]

merged["Student ID"] = pd.to_numeric(merged["Student ID"], errors='coerce').astype("Int64")
merged["student_name"] = pd.to_numeric(merged["student_name"], errors='coerce').astype("Int64")
merged["gender"] = pd.to_numeric(merged["gender"], errors='coerce').astype("Int64")
merged["grade"] = pd.to_numeric(merged["grade"], errors='coerce').astype("Int64")
merged["reading_score"] = pd.to_numeric(merged["reading_score"], errors='coerce').astype("Int64")
merged["math_score"] = pd.to_numeric(merged["math_score"], errors='coerce').astype("Int64")
merged["School ID"] = pd.to_numeric(merged["School ID"], errors='coerce').astype("Int64")
merged["type"] = pd.to_numeric(merged["type"], errors='coerce').astype("Int64")
merged["size"] = pd.to_numeric(merged["size"], errors='coerce').astype("Int64")
merged["budget"] = pd.to_numeric(merged["budget"], errors='coerce').astype("Int64")

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_27/target_multisource_mcts.csv", index=False)