import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Rename year columns to persist columns
s0 = s0.rename(columns={'year 2016': 'persist 2016'})
s1 = s1.rename(columns={'year 2014': 'persist 2014'})
s3 = s3.rename(columns={'year 2015': 'persist 2015'})

# Join s0 and s1 on Institution (inner join)
join_01 = pd.merge(s0, s1, on='Institution', how='inner')

# Join the above with s3 on Institution (inner join)
join_013 = pd.merge(join_01, s3, on='Institution', how='inner')

# Join with s2 (Fall data) on Institution (inner join)
join_0132 = pd.merge(join_013, s2, on='Institution', how='inner')

# Join with s4 (Cohort data) on Institution (inner join)
join_all = pd.merge(join_0132, s4, on='Institution', how='inner')

# Group by Institution to ensure unique rows (no aggregation needed as keys are unique)
result = join_all.groupby('Institution', as_index=False).first()

# Select and reorder columns as per target schema
cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
        'persist 2014', 'persist 2015', 'persist 2016',
        'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

result = result[cols]

# Convert columns to correct types
result['persist 2014'] = pd.to_numeric(result['persist 2014'], errors='coerce').astype('Int64')
result['persist 2015'] = pd.to_numeric(result['persist 2015'], errors='coerce').astype('Int64')
result['persist 2016'] = pd.to_numeric(result['persist 2016'], errors='coerce').astype('Int64')
result['Cohort 2014'] = pd.to_numeric(result['Cohort 2014'], errors='coerce').astype('Int64')
result['Cohort 2015'] = pd.to_numeric(result['Cohort 2015'], errors='coerce').astype('Int64')
result['Cohort 2016'] = pd.to_numeric(result['Cohort 2016'], errors='coerce').astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)