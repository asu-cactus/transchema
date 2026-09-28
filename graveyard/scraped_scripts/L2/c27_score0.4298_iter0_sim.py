import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_27/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_27/training_1.csv", index_col=0)

df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

df_merged = df_merged.rename(columns={
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

df_merged = df_merged[[
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

df_merged["Student ID"] = df_merged["Student ID"].astype(int)
df_merged["student_name"] = df_merged["student_name"].astype(str)
df_merged["gender"] = df_merged["gender"].astype(str)
df_merged["grade"] = df_merged["grade"].astype(str)
df_merged["reading_score"] = df_merged["reading_score"].astype(int)
df_merged["math_score"] = df_merged["math_score"].astype(int)
df_merged["School ID"] = df_merged["School ID"].astype(int)
df_merged["type"] = df_merged["type"].astype(str)
df_merged["size"] = df_merged["size"].astype(int)
df_merged["budget"] = df_merged["budget"].astype(int)

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_27/target_multisource_mcts.csv", index=False)