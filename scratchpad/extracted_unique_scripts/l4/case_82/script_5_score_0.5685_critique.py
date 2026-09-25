import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Rename year columns in s0, s1, s3 to match target persist columns
s0 = s0.rename(columns={"year 2016": "persist 2016"})
s1 = s1.rename(columns={"year 2014": "persist 2014"})
s3 = s3.rename(columns={"year 2015": "persist 2015"})

# Join s0, s1, s3 on Institution
joined_013 = s0.merge(s1, on="Institution", how="outer").merge(s3, on="Institution", how="outer")

# Join with s2 (Fall columns)
joined_0132 = joined_013.merge(s2, on="Institution", how="outer")

# Join with s4 (Cohort columns)
final_joined = joined_0132.merge(s4, on="Institution", how="outer")

# Convert columns to appropriate types
# Fall columns: float
for c in ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']:
    final_joined[c] = pd.to_numeric(final_joined[c], errors='coerce')

# persist and Cohort columns: integer (nullable Int64)
for c in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    final_joined[c] = pd.to_numeric(final_joined[c], errors='coerce').astype('Int64')

# Group by Institution to ensure uniqueness and aggregate duplicates
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

final = final_joined.groupby('Institution', as_index=False).agg(agg_dict)

# Ensure integer columns are Int64 after aggregation (sum returns int64)
for c in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    final[c] = final[c].astype('Int64')

# Reorder columns to match target schema
cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
        'persist 2014', 'persist 2015', 'persist 2016',
        'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

final = final[cols]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)