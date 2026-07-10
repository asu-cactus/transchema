import pandas as pd

# Read source tables with index_col=0 to ignore the first column as per instructions
df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

# Perform a left join on school_name to preserve all students
merged = pd.merge(df_students, df_schools, on="school_name", how="left")

# Select and order columns exactly as in the target schema
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

# Cast columns to the correct types as per target schema
merged["Student ID"] = merged["Student ID"].astype(int)
merged["reading_score"] = merged["reading_score"].astype(int)
merged["math_score"] = merged["math_score"].astype(int)
merged["School ID"] = merged["School ID"].astype(int)
merged["size"] = merged["size"].astype(int)
merged["budget"] = merged["budget"].astype(int)

# Write the output CSV without the index
merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)