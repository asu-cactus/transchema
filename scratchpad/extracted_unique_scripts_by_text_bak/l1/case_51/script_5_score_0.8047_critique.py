import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_51/target_multisource_mcts.csv"

# Read source tables with index_col=0 to ignore the first index column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on 'school_name'
merged = df0.merge(df1, on="school_name", how="left")

# Select columns in target schema order
final = merged[[
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

# Convert columns to appropriate types
final = final.astype({
    "Student ID": "Int64",
    "reading_score": "Int64",
    "math_score": "Int64",
    "School ID": "Int64",
    "size": "Int64",
    "budget": "Int64"
})

# Write to target CSV without index
final.to_csv(target_path, index=False)