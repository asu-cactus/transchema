import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_17/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_17/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_17/target_multisource_mcts.csv"

# Read source tables with index_col=0 to ignore the first index column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on school_name (foreign key relationship)
merged = pd.merge(df0, df1, on="school_name", how="inner")

# Drop any extra index columns that may appear after merge
if 'Unnamed: 0' in merged.columns:
    merged = merged.drop(columns=['Unnamed: 0'])

# Select columns exactly as in target schema
final_cols = ['School ID', 'school_name', 'type', 'size', 'budget',
              'Student ID', 'student_name', 'gender', 'grade', 'reading_score', 'math_score']

result = merged[final_cols]

# Write to CSV without index
result.to_csv(target_path, index=False)