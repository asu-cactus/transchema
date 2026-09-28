import pandas as pd

df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_0.csv", index_col=0)
df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv", index_col=0)

df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

df_result = df_merged[[
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

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts.csv", index=False)