import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_51/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Normalize school_name columns to ensure matching keys
df0['school_name'] = df0['school_name'].str.strip().str.lower()
df1['school_name'] = df1['school_name'].str.strip().str.lower()

df = pd.merge(df0, df1, on="school_name", how="inner")

# Restore original casing of school_name from df0 (assuming df0 has correct casing)
# Since we lowered school_name for join, replace with original from df0
df['school_name'] = df0.set_index('Student ID').loc[df['Student ID'], 'school_name'].values

# Reorder columns as per target schema
df = df[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score',
         'School ID', 'type', 'size', 'budget']]

# Convert columns to correct types without assignment
df['Student ID'] = df['Student ID'].astype(int)
df['reading_score'] = df['reading_score'].astype(int)
df['math_score'] = df['math_score'].astype(int)
df['School ID'] = df['School ID'].astype(int)
df['size'] = df['size'].astype(int)
df['budget'] = df['budget'].astype(int)

df.to_csv(target_path, index=False)