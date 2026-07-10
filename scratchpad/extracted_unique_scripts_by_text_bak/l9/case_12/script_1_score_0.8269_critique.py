import pandas as pd

# Read all source tables
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
# We keep '2012-12-05' as is, and rename the value column to the target column name

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

# Perform inner joins on '2012-12-05' to keep only dates present in all sources
df = s0.merge(s1, on='2012-12-05', how='inner') \
       .merge(s2, on='2012-12-05', how='inner') \
       .merge(s3, on='2012-12-05', how='inner') \
       .merge(s4, on='2012-12-05', how='inner') \
       .merge(s5, on='2012-12-05', how='inner') \
       .merge(s6, on='2012-12-05', how='inner') \
       .merge(s7, on='2012-12-05', how='inner') \
       .merge(s8, on='2012-12-05', how='inner') \
       .merge(s9, on='2012-12-05', how='inner') \
       .merge(s10, on='2012-12-05', how='inner')

# Cast columns to correct types as per target schema
df = df.astype({
    '2012-12-05': str,
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

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)