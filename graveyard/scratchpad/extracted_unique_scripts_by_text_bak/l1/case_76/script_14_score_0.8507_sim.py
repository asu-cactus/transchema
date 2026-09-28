import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

agg = df0.groupby("Student ID").agg({
    "student_name": "min",
    "gender": "min",
    "grade": "min",
    "school_name": "min",
    "reading_score": "mean",
    "math_score": "mean"
}).reset_index()

merged = pd.merge(agg, df1, how="inner", on="school_name")

merged["reading_score"] = merged["reading_score"].round().astype("Int64")
merged["math_score"] = merged["math_score"].round().astype("Int64")

result = merged[[
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

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)