import pandas as pd

s0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv', index_col=0)
s1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv', index_col=0)
s2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv', index_col=0)
s3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv', index_col=0)
s4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv', index_col=0)

agg0 = s0.groupby('Institution', as_index=False)['year 2016'].sum()
agg1 = s1.groupby('Institution', as_index=False)['year 2014'].sum()
agg3 = s3.groupby('Institution', as_index=False)['year 2015'].sum()
agg4_cohort = s4.groupby('Institution', as_index=False)[['Cohort 2014', 'Cohort 2015', 'Cohort 2016']].sum()

df = agg0.merge(agg1, on='Institution', how='outer')
df = df.merge(agg3, on='Institution', how='outer')
df = df.merge(agg4_cohort, on='Institution', how='outer')

df = df.merge(s2, on='Institution', how='outer')

df['persist 2014'] = 0
df['persist 2015'] = 0
df['persist 2016'] = 0

df = df.rename(columns={
    'year 2016': '(Fall 2016)',  # but target schema has no (Fall 2016), so drop or ignore
    'year 2014': '(Fall 2014)',  # but s1 year 2014 is a year, target has (Fall 2014) float, so we keep s2's (Fall 2014)
    'year 2015': '(Fall 2015)',  # target has no (Fall 2015), so drop
})

# Drop columns not in target schema
drop_cols = ['year 2016', 'year 2014', 'year 2015', '(Fall 2015)', '(Fall 2016)']
for c in drop_cols:
    if c in df.columns:
        df = df.drop(columns=c)

# Select and reorder columns as per target schema
cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
        'persist 2014', 'persist 2015', 'persist 2016',
        'Cohort 2014', 'Cohort 2015', 'Cohort 2016']

df = df[cols]

df['persist 2014'] = df['persist 2014'].astype('Int64')
df['persist 2015'] = df['persist 2015'].astype('Int64')
df['persist 2016'] = df['persist 2016'].astype('Int64')

df['Cohort 2014'] = df['Cohort 2014'].astype('Int64')
df['Cohort 2015'] = df['Cohort 2015'].astype('Int64')
df['Cohort 2016'] = df['Cohort 2016'].astype('Int64')

df.to_csv('autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv', index=False)