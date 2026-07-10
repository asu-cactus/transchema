import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv"

# Read CSVs without index_col=0 to keep all columns intact
df0 = pd.read_csv(source0_path)
df1 = pd.read_csv(source1_path)

# Join on school_name
merged = pd.merge(df0, df1, on="school_name", how="inner")

# Reorder columns to match target schema
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

# Cast columns to correct types
merged = merged.astype({
    "Student ID": int,
    "reading_score": int,
    "math_score": int,
    "School ID": int,
    "size": int,
    "budget": int
})

# Write to target CSV without index
merged.to_csv(target_path, index=False)