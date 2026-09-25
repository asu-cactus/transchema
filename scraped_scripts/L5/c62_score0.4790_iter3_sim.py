import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_62/training_4.csv", index_col=0)

dfs = [df0, df1, df2, df3, df4]

for i, df in enumerate(dfs):
    df.rename(columns={
        "Don't know/Refused/Missing": "Don't know/Refused/Missing",
        "Normal Weight": "Normal Weight",
        "Obese": "Obese",
        "Overweight": "Overweight",
        "Underweight": "Underweight"
    }, inplace=True)

# Merge all on ['Sex', 'Age Group'] with outer join to keep all keys
from functools import reduce

def merge_dfs(left, right):
    return pd.merge(left, right, on=['Sex', 'Age Group'], how='outer', suffixes=('', '_dup'))

merged = reduce(merge_dfs, dfs)

# After merge, columns with suffix '_dup' are duplicates from other dfs
# We need to sum all columns with same base name across all dfs

base_cols = ["Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]

result = merged[['Sex', 'Age Group']].copy()

for col in base_cols:
    # Collect all columns that start with col (including col itself and col_dup, col_dup_dup, etc)
    col_variants = [c for c in merged.columns if c == col or c.startswith(col + '_')]
    # Sum all these columns row-wise, ignoring NaNs
    result[col] = merged[col_variants].sum(axis=1, skipna=True).astype('Int64')

# Convert 'Age Group' from string like 'Age 18 to 24' to integer 18 (start age)
def extract_start_age(age_group_str):
    if pd.isna(age_group_str):
        return pd.NA
    parts = age_group_str.split()
    for part in parts:
        if part.isdigit():
            return int(part)
    return pd.NA

result['Age Group'] = result['Age Group'].apply(extract_start_age).astype('Int64')

result = result[['Sex', 'Age Group', "Don't know/Refused/Missing", "Normal Weight", "Obese", "Overweight", "Underweight"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_62/target_multisource_mcts.csv", index=False)