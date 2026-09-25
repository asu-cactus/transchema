import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

# Join on school_name (case-sensitive as no hint to normalize)
merged = pd.merge(df0, df1, on="school_name", how="inner")

# Group by Student ID to ensure uniqueness (no aggregation needed, just drop duplicates)
merged = merged.groupby("Student ID", as_index=False).first()

# Select columns in target schema order
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