import pandas as pd

# Read all source CSVs with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
union_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'Subject' to integer if possible, else leave as is
def try_convert_subject(x):
    try:
        return int(x)
    except:
        return x

union_df['Subject'] = union_df['Subject'].apply(try_convert_subject)

# Group by leftmost columns: 'Split', 'SubjectId', 'Subject'
# Aggregate by sum for all numeric columns
result = union_df.groupby(['Split', 'SubjectId', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

# Ensure types match target schema
result['Split'] = result['Split'].astype(str)
result['SubjectId'] = result['SubjectId'].astype(int)
# 'Subject' may be int or string, but target expects int, so convert if possible
result['Subject'] = result['Subject'].apply(try_convert_subject)
if result['Subject'].dtype != 'int64':
    try:
        result['Subject'] = result['Subject'].astype(int)
    except:
        pass

# Reorder columns exactly as target schema
result = result[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)