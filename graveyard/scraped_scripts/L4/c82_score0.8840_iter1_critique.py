import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Join persist year tables on Institution (inner join to keep only matching Institutions)
persist = s0.merge(s1, on="Institution", how="inner").merge(s3, on="Institution", how="inner")

# Rename year columns to persist columns
persist = persist.rename(columns={
    "year 2014": "persist 2014",
    "year 2015": "persist 2015",
    "year 2016": "persist 2016"
})

# Join persist data with Fall data (s2) on Institution (inner join)
df = persist.merge(s2, on="Institution", how="inner")

# Join with Cohort data (s4) on Institution (inner join)
df = df.merge(s4, on="Institution", how="inner")

# Convert persist and Cohort columns to numeric (integer)
for col in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Group by Institution and aggregate
agg_dict = {
    '(Fall 2011)': 'mean',
    '(Fall 2012)': 'mean',
    '(Fall 2013)': 'mean',
    '(Fall 2014)': 'mean',
    'persist 2014': 'sum',
    'persist 2015': 'sum',
    'persist 2016': 'sum',
    'Cohort 2014': 'sum',
    'Cohort 2015': 'sum',
    'Cohort 2016': 'sum'
}

result = df.groupby('Institution', as_index=False).agg(agg_dict)

# Ensure columns order as target schema
target_cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
               'persist 2014', 'persist 2015', 'persist 2016',
               'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

result = result[target_cols]

# Persist and Cohort columns to Int64 again after aggregation (sum may produce int64)
for col in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    result[col] = pd.to_numeric(result[col], errors='coerce').astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)