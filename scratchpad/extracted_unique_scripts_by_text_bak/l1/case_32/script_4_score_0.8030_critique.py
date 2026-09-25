import pandas as pd

# Read sources with index_col=0 as instructed
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_32/training_1.csv", index_col=0)

# Normalize school_name in both tables for consistent join
source0['school_name'] = source0['school_name'].str.strip().str.lower()
source1['school_name'] = source1['school_name'].str.strip().str.lower()

# Join on normalized school_name with inner join to ensure matching rows only
merged = pd.merge(source1, source0, on='school_name', how='inner')

# After join, restore school_name to original case from source1 (optional)
# But since target examples have school_name capitalized, we can capitalize each word
merged['school_name'] = merged['school_name'].str.title()

# Select columns in target schema order
cols = ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']
result = merged[cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_32/target_multisource_mcts.csv", index=False)