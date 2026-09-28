import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_47/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_47/training_1.csv", index_col=0)

# Normalize school_name in both dataframes to ensure matching join keys
df_students["school_name"] = df_students["school_name"].str.strip().str.lower()
df_schools["school_name"] = df_schools["school_name"].str.strip().str.lower()

# Perform inner join on normalized school_name
df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

# Restore original casing of school_name from students table by mapping back
# Create a mapping from normalized to original school_name in students
school_name_map = df_students[["school_name"]].drop_duplicates()
school_name_map["school_name_original"] = df_students["school_name"].str.strip()
# Actually, better to just use the original school_name from students before normalization:
# So we keep a copy before normalization:
df_students_orig = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_47/training_0.csv", index_col=0)
df_merged["school_name"] = df_merged["school_name"].map(
    df_students_orig.set_index("school_name")["school_name"]
).fillna(df_merged["school_name"])

# Select and reorder columns as per target schema
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

# Cast columns to correct types
df_merged["Student ID"] = df_merged["Student ID"].astype(int)
df_merged["reading_score"] = df_merged["reading_score"].astype(int)
df_merged["math_score"] = df_merged["math_score"].astype(int)
df_merged["School ID"] = df_merged["School ID"].astype(int)
df_merged["size"] = df_merged["size"].astype(int)
df_merged["budget"] = df_merged["budget"].astype(int)

# Write output
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_47/target_multisource_mcts.csv", index=False)