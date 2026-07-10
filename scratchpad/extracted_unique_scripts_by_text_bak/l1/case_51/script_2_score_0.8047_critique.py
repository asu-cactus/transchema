import pandas as pd

# Read source tables with index_col=0 as instructed
df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_51/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_51/training_1.csv", index_col=0)

# Normalize school_name columns to ensure join correctness (strip spaces and lowercase)
df_students["school_name"] = df_students["school_name"].str.strip()
df_schools["school_name"] = df_schools["school_name"].str.strip()

# Perform inner join on school_name
df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

# Reorder columns to match target schema exactly
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

# Ensure correct data types as per target schema
df_merged["Student ID"] = df_merged["Student ID"].astype(int)
df_merged["reading_score"] = df_merged["reading_score"].astype(int)
df_merged["math_score"] = df_merged["math_score"].astype(int)
df_merged["School ID"] = df_merged["School ID"].astype(int)
df_merged["size"] = df_merged["size"].astype(int)
df_merged["budget"] = df_merged["budget"].astype(int)

# Write output to target file
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_51/target_multisource_mcts.csv", index=False)