import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
df10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

# Aggregate df0 by summing '301.0' per date
agg_df0 = df0.groupby('2012-12-05', as_index=False)['301.0'].sum()

# Join all other dataframes on '2012-12-05' using inner join to keep only matching dates
joined = agg_df0.merge(df1, on='2012-12-05', how='inner') \
                .merge(df2, on='2012-12-05', how='inner') \
                .merge(df3, on='2012-12-05', how='inner') \
                .merge(df4, on='2012-12-05', how='inner') \
                .merge(df5, on='2012-12-05', how='inner') \
                .merge(df6, on='2012-12-05', how='inner') \
                .merge(df7, on='2012-12-05', how='inner') \
                .merge(df8, on='2012-12-05', how='inner') \
                .merge(df9, on='2012-12-05', how='inner') \
                .merge(df10, on='2012-12-05', how='inner')

# Cast columns to correct types as per target schema
joined = joined.astype({
    '2012-12-05': str,
    '301.0': 'Int64',
    '0.0075805085': 'float',
    '0.0179': 'float',
    '6.9': 'float',
    '0.17657143': 'float',
    '20.3333': 'float',
    '0.016157143': 'float',
    '242.364': 'float',
    '0.1646': 'float',
    '0.7268': 'float',
    '0.4332': 'float'
})

# Write final output
joined.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)