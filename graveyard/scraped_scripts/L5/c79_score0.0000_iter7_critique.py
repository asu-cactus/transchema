import pandas as pd

# Read all source CSVs with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv", index_col=0)

# UNION all sources (concatenate)
df = pd.concat([source0, source1, source2, source3, source4], ignore_index=True)

# Columns in target schema
target_cols = ['Initiator', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']

# Ensure all columns exist in df (they do), reorder columns to target schema
df = df[target_cols]

# Group by Initiator and WarID (leftmost string and int columns)
group_by_cols = ['Initiator', 'WarID']

# Aggregation columns are all other columns except group_by_cols
agg_cols = [col for col in target_cols if col not in group_by_cols]

# Aggregate by sum for all aggregation columns
agg_dict = {col: 'sum' for col in agg_cols}

# Perform groupby and aggregation
result = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# The target schema expects integer columns, convert floats to int where possible
# Some columns may have NaN, fill NaN with 0 before converting to int
for col in agg_cols:
    result[col] = result[col].fillna(0).astype(int)

# Save to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)