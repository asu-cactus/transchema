import pandas as pd

df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_0.csv", index_col=0)
df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv", index_col=0)

# Normalize school_name strings in both dataframes for consistent join
df_schools['school_name'] = df_schools['school_name'].str.strip().str.lower()
df_students['school_name'] = df_students['school_name'].str.strip().str.lower()

df_merged = pd.merge(df_students, df_schools, on="school_name", how="inner")

# Restore original casing of school_name from students table by mapping back
# (optional, but target examples show original casing)
# Since we normalized to lowercase, we can map back using students original values:
# Create a mapping from lowercase to original school_name in students
school_name_map = df_students[['school_name']].drop_duplicates()
# But since we already replaced school_name in df_students, we lost original casing.
# So better to keep original school_name before normalization:
# Let's reload students again to get original school_name for output

df_students_orig = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv", index_col=0)
df_students_orig['school_name_lower'] = df_students_orig['school_name'].str.strip().str.lower()

# Merge original school_name back to df_merged on Student ID
df_merged = df_merged.merge(
    df_students_orig[['Student ID', 'school_name', 'school_name_lower']],
    left_on=['Student ID', 'school_name'],
    right_on=['Student ID', 'school_name_lower'],
    how='left',
    suffixes=('', '_orig')
)

# Replace normalized school_name with original casing
df_merged['school_name'] = df_merged['school_name_orig']

df_result = df_merged[[
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

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts.csv", index=False)