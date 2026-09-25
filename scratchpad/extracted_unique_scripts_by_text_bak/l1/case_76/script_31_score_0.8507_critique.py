import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv", index_col=0)

# Normalize join keys to avoid mismatches due to case or whitespace
df0['school_name'] = df0['school_name'].str.strip().str.lower()
df1['school_name'] = df1['school_name'].str.strip().str.lower()

# Join on normalized school_name with inner join
merged = pd.merge(df0, df1, on='school_name', how='inner')

# Restore original casing of school_name from df0 (assuming df0 has correct casing)
# Since we joined on lowercased keys, the merged 'school_name' is lowercased.
# We can map back to original casing by merging with df0 original school_name:
# But since df0['school_name'] was overwritten, we can do this by:
# Create a mapping from lowercased to original school_name from df0 before normalization
# So redo normalization with a copy to keep original school_name

df0_orig = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv", index_col=0)
mapping = df0_orig[['school_name']].copy()
mapping['school_name_lower'] = mapping['school_name'].str.strip().str.lower()
mapping = mapping.drop_duplicates(subset=['school_name_lower'])
mapping_dict = mapping.set_index('school_name_lower')['school_name'].to_dict()

# Replace lowercased school_name in merged with original casing
merged['school_name'] = merged['school_name'].map(mapping_dict)

# Select columns in target schema order
result = merged[[
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

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv", index=False)