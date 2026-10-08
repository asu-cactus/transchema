import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_27/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_27/training_1.csv", index_col=0)

# Join on school_name
df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

# Group by school_name and aggregate counts for all other columns
df_grouped = df_merged.groupby("school_name").agg({
    "Student ID": "count",
    "student_name": "count",
    "gender": "count",
    "grade": "count",
    "reading_score": "count",
    "math_score": "count",
    "School ID": "count",
    "type": "count",
    "size": "count",
    "budget": "count"
}).reset_index()

# Rename columns to match target schema exactly
df_grouped = df_grouped.rename(columns={
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

# Ensure correct dtypes as per target schema
df_grouped["school_name"] = df_grouped["school_name"].astype(str)
df_grouped["Student ID"] = df_grouped["Student ID"].astype(int)
df_grouped["student_name"] = df_grouped["student_name"].astype(int)
df_grouped["gender"] = df_grouped["gender"].astype(int)
df_grouped["grade"] = df_grouped["grade"].astype(int)
df_grouped["reading_score"] = df_grouped["reading_score"].astype(int)
df_grouped["math_score"] = df_grouped["math_score"].astype(int)
df_grouped["School ID"] = df_grouped["School ID"].astype(int)
df_grouped["type"] = df_grouped["type"].astype(int)
df_grouped["size"] = df_grouped["size"].astype(int)
df_grouped["budget"] = df_grouped["budget"].astype(int)

# Reorder columns exactly as target schema
df_grouped = df_grouped[[
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

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_27/target_multisource_mcts.csv", index=False)