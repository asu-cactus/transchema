import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts.csv"

# Read source0 without setting index_col=0 to keep 'School ID' as a column
df0 = pd.read_csv(source0_path)
# Read source1 similarly
df1 = pd.read_csv(source1_path)

# Merge on 'school_name' (inner join)
merged = pd.merge(df1, df0, how="inner", on="school_name")

# Select columns in the exact order as target schema
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

# Write to target path without index
merged.to_csv(target_path, index=False)