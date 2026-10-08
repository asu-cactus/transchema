import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name", how="inner")

merged = merged.rename(columns={
    "Student ID": "Student ID",
    "student_name": "student_name",
    "gender": "gender",
    "grade": "grade",
    "school_name": "school_name",
    "reading_score": "reading_score",
    "math_score": "math_score",
    "School ID": "School ID",
    "type": "type",
    "size": "size",
    "budget": "budget"
})

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

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)