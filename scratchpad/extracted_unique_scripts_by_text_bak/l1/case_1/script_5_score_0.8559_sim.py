import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_1/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_1/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_1/target_multisource_mcts.csv"

df_students = pd.read_csv(source0_path, index_col=0)
df_schools = pd.read_csv(source1_path, index_col=0)

df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

df_merged = df_merged.rename(columns={"School ID": "School ID"})

df_merged = df_merged[[
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

df_merged.to_csv(target_path, index=False)