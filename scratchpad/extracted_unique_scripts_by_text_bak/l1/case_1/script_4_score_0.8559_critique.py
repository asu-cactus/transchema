import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_1/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_1/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_1/target_multisource_mcts.csv"

df_students = pd.read_csv(source0_path, index_col=0)
df_schools = pd.read_csv(source1_path, index_col=0)

# Join on school_name
df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

# Group by Student ID to ensure uniqueness, aggregate other columns by first
df_grouped = df_merged.groupby('Student ID', as_index=False).agg({
    'student_name': 'first',
    'gender': 'first',
    'grade': 'first',
    'school_name': 'first',
    'reading_score': 'first',
    'math_score': 'first',
    'School ID': 'first',
    'type': 'first',
    'size': 'first',
    'budget': 'first'
})

# Ensure correct types
df_grouped['Student ID'] = df_grouped['Student ID'].astype(int)
df_grouped['reading_score'] = df_grouped['reading_score'].astype(int)
df_grouped['math_score'] = df_grouped['math_score'].astype(int)
df_grouped['School ID'] = df_grouped['School ID'].astype(int)
df_grouped['size'] = df_grouped['size'].astype(int)
df_grouped['budget'] = df_grouped['budget'].astype(int)

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']]

df_grouped.to_csv(target_path, index=False)