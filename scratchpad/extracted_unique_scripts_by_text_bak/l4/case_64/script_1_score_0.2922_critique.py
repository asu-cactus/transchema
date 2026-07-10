import pandas as pd
import numpy as np

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_3.csv', index_col=0)

# All source tables have similar schema, union them
df = pd.concat([source0, source1, source2, source3], ignore_index=True)

# Define group by columns (leftmost non-float unique columns in target)
group_by_cols = ['grade_range_cd_9-12', 'student_num', 'lea_avg_student_num', 'st_avg_student_num']

# Determine columns to aggregate (all except group_by_cols)
agg_cols = [col for col in df.columns if col not in group_by_cols]

# We need to decide aggregation function per column:
# - Columns with float values between 0 and 1 or percentages: mean
# - Columns with integer counts or totals: sum
# - Columns with scores (usually integer but can be float): mean

# To decide, we check data types and value ranges:
# For simplicity, treat columns with float dtype or with max <=1 as mean, else sum

# Identify columns with float dtype
float_cols = df.select_dtypes(include=['float64', 'float32']).columns.tolist()

# Also, some int columns with values between 0 and 1 (percentages) should be mean
# So check columns with max <=1 (or close) and min >=0, treat as mean
mean_cols = set(float_cols)  # start with float columns

for col in agg_cols:
    if col not in mean_cols:
        # Check if numeric
        if pd.api.types.is_numeric_dtype(df[col]):
            col_max = df[col].max()
            col_min = df[col].min()
            # If values between 0 and 1 (or close), treat as mean
            if 0 <= col_min and col_max <= 1.1:
                mean_cols.add(col)

# The rest are sum columns
sum_cols = [col for col in agg_cols if col not in mean_cols]

# Build aggregation dictionary
agg_dict = {}
for col in mean_cols:
    agg_dict[col] = 'mean'
for col in sum_cols:
    agg_dict[col] = 'sum'

# Perform group by and aggregation
result = df.groupby(group_by_cols, dropna=False).agg(agg_dict).reset_index()

# After aggregation, cast all columns to int as target schema is integer
# For mean columns, round before casting
for col in mean_cols:
    result[col] = result[col].round().astype('Int64')  # Use nullable integer type to allow NaNs

for col in sum_cols:
    result[col] = result[col].astype('Int64')

# Ensure group_by columns are also Int64 (nullable int)
for col in group_by_cols:
    result[col] = result[col].astype('Int64')

# Write to output file
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_64/target_multisource_mcts.csv', index=False)