import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)  # year 2016
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)  # year 2014
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)  # Fall years
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)  # year 2015
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)  # Cohort years

# Process fall years 2011-2014 from s2
fall_cols = ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']
fall_pivot = s2[['Institution'] + fall_cols].copy()

# Join persist columns from s1, s3, s0 on Institution using inner joins
persist = s1[['Institution', 'year 2014']].merge(
    s3[['Institution', 'year 2015']], on='Institution', how='inner').merge(
    s0[['Institution', 'year 2016']], on='Institution', how='inner')

persist = persist.rename(columns={
    'year 2014': 'persist 2014',
    'year 2015': 'persist 2015',
    'year 2016': 'persist 2016'
})

# Join fall_pivot and persist on Institution using inner join
df = fall_pivot.merge(persist, on='Institution', how='inner')

# Join cohort data s4 on Institution using inner join
df = df.merge(s4, on='Institution', how='inner')

# Convert types to match target schema
for col in fall_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

for col in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Group by Institution to ensure unique rows (no aggregation needed)
df = df.groupby('Institution', as_index=False).first()

# Reorder columns exactly as target schema
df = df[['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
         'persist 2014', 'persist 2015', 'persist 2016',
         'Cohort 2014', 'Cohort 2015', 'Cohort 2016']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)