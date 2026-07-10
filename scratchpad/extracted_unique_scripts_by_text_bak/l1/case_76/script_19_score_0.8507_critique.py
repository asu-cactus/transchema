import pandas as pd

# Read source tables with index_col=0 to ignore the first column (index)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

# Normalize school_name columns by stripping whitespace to ensure correct join
df0['school_name'] = df0['school_name'].str.strip()
df1['school_name'] = df1['school_name'].str.strip()

# Perform inner join on school_name
merged = pd.merge(df0, df1, on="school_name", how="inner")

# Select columns in the exact order as target schema
cols = ['Student ID', 'student_name', 'gender', 'grade', 'school_name',
        'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']

result = merged[cols]

# Write to output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)