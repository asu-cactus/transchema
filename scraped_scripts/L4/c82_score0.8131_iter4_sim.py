import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

fall_cols = ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']
unpivot = s2.melt(id_vars=['Institution'], value_vars=fall_cols, var_name='Year', value_name='Fall_Rate')

s1_renamed = s1.rename(columns={'year 2014': 'persist 2014'})
s3_renamed = s3.rename(columns={'year 2015': 'persist 2015'})
s0_renamed = s0.rename(columns={'year 2016': 'persist 2016'})

df = unpivot.merge(s1_renamed, on='Institution', how='left')
df = df.merge(s3_renamed, on='Institution', how='left')
df = df.merge(s0_renamed, on='Institution', how='left')
df = df.merge(s4, on='Institution', how='left')

pivot = df.pivot_table(index='Institution', columns='Year', values='Fall_Rate', aggfunc='max').reset_index()

pivot = pivot.rename(columns={
    '(Fall 2011)': '(Fall 2011)',
    '(Fall 2012)': '(Fall 2012)',
    '(Fall 2013)': '(Fall 2013)',
    '(Fall 2014)': '(Fall 2014)'
})

result = pivot.merge(s1_renamed[['Institution', 'persist 2014']], on='Institution', how='left')
result = result.merge(s3_renamed[['Institution', 'persist 2015']], on='Institution', how='left')
result = result.merge(s0_renamed[['Institution', 'persist 2016']], on='Institution', how='left')
result = result.merge(s4, on='Institution', how='left')

result = result[['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
                 'persist 2014', 'persist 2015', 'persist 2016',
                 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']]

result['persist 2014'] = result['persist 2014'].astype('Int64')
result['persist 2015'] = result['persist 2015'].astype('Int64')
result['persist 2016'] = result['persist 2016'].astype('Int64')
result['Cohort 2014'] = result['Cohort 2014'].astype('Int64')
result['Cohort 2015'] = result['Cohort 2015'].astype('Int64')
result['Cohort 2016'] = result['Cohort 2016'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)