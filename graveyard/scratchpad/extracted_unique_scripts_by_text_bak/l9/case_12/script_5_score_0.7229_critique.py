import pandas as pd

# Read all source CSVs
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

# Rename columns to match target schema exactly
# Each source has columns: ['2012-12-05', <value_column>]
# We rename the value column to the target column name (second column in target schema)
s0.columns = ['2012-12-05', '301.0']
s1.columns = ['2012-12-05', '0.016157143']
s2.columns = ['2012-12-05', '242.364']
s3.columns = ['2012-12-05', '0.1646']
s4.columns = ['2012-12-05', '0.4332']
s5.columns = ['2012-12-05', '20.3333']
s6.columns = ['2012-12-05', '0.0075805085']
s7.columns = ['2012-12-05', '6.9']
s8.columns = ['2012-12-05', '0.0179']
s9.columns = ['2012-12-05', '0.17657143']
s10.columns = ['2012-12-05', '0.7268']

# Merge all sources on '2012-12-05' using outer join to keep all dates
df = s0.merge(s1, on='2012-12-05', how='outer') \
       .merge(s2, on='2012-12-05', how='outer') \
       .merge(s3, on='2012-12-05', how='outer') \
       .merge(s4, on='2012-12-05', how='outer') \
       .merge(s5, on='2012-12-05', how='outer') \
       .merge(s6, on='2012-12-05', how='outer') \
       .merge(s7, on='2012-12-05', how='outer') \
       .merge(s8, on='2012-12-05', how='outer') \
       .merge(s9, on='2012-12-05', how='outer') \
       .merge(s10, on='2012-12-05', how='outer')

# Convert '2012-12-05' to string (date as string)
df['2012-12-05'] = df['2012-12-05'].astype(str)

# Aggregate: group by '2012-12-05'
# sum aggregation for '301.0' (integer column)
# mean aggregation for all other float columns
agg_dict = {
    '301.0': 'sum',
    '0.0075805085': 'mean',
    '0.0179': 'mean',
    '6.9': 'mean',
    '0.17657143': 'mean',
    '20.3333': 'mean',
    '0.016157143': 'mean',
    '242.364': 'mean',
    '0.1646': 'mean',
    '0.7268': 'mean',
    '0.4332': 'mean'
}

df = df.groupby('2012-12-05', as_index=False).agg(agg_dict)

# Cast '301.0' to integer type (nullable Int64)
df = df.astype({
    '301.0': 'Int64',
    '0.0075805085': float,
    '0.0179': float,
    '6.9': float,
    '0.17657143': float,
    '20.3333': float,
    '0.016157143': float,
    '242.364': float,
    '0.1646': float,
    '0.7268': float,
    '0.4332': float
})

# Write to CSV without index
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)