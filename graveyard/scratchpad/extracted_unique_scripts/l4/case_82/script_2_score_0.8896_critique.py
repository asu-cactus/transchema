import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Join source2 (Fall data) with source1 (year 2014 persist)
df = pd.merge(source2, source1, on='Institution', how='inner')

# Join with source3 (year 2015 persist)
df = pd.merge(df, source3, on='Institution', how='inner')

# Join with source0 (year 2016 persist)
df = pd.merge(df, source0, on='Institution', how='inner')

# Join with source4 (Cohort data)
df = pd.merge(df, source4, on='Institution', how='inner')

# Rename year columns to persist columns
df = df.rename(columns={
    'year 2014': 'persist 2014',
    'year 2015': 'persist 2015',
    'year 2016': 'persist 2016'
})

# Select columns exactly as target schema
df = df[['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
         'persist 2014', 'persist 2015', 'persist 2016',
         'Cohort 2014', 'Cohort 2015', 'Cohort 2016']]

# Cast integer columns to Int64 (nullable integer)
df['persist 2014'] = df['persist 2014'].astype('Int64')
df['persist 2015'] = df['persist 2015'].astype('Int64')
df['persist 2016'] = df['persist 2016'].astype('Int64')
df['Cohort 2014'] = df['Cohort 2014'].astype('Int64')
df['Cohort 2015'] = df['Cohort 2015'].astype('Int64')
df['Cohort 2016'] = df['Cohort 2016'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)