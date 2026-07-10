import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

fall_cols = ['(Fall 2000)', '(Fall 2001)', '(Fall 2002)', '(Fall 2003)', '(Fall 2004)', '(Fall 2005)', '(Fall 2006)', '(Fall 2007)', '(Fall 2008)', '(Fall 2009)', '(Fall 2010)', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']
unpivot = s2.melt(id_vars=['Institution'], value_vars=fall_cols, var_name='year', value_name='value')

unpivot['year'] = unpivot['year'].str.strip('()').str.replace('Fall ', '').astype(int)
s1_renamed = s1.rename(columns={'year 2014': 'year_2014'})
s3_renamed = s3.rename(columns={'year 2015': 'year_2015'})
s0_renamed = s0.rename(columns={'year 2016': 'year_2016'})

# Filter unpivot to years 2011-2014 for target columns
unpivot_filtered = unpivot[unpivot['year'].isin([2011,2012,2013,2014])]

# Pivot unpivot_filtered to wide format for Fall years 2011-2014
fall_pivot = unpivot_filtered.pivot(index='Institution', columns='year', values='value').reset_index()
fall_pivot.columns = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']

# Join persist columns from s1, s3, s0 on Institution
persist = s1[['Institution', 'year 2014']].merge(s3[['Institution', 'year 2015']], on='Institution', how='outer').merge(s0[['Institution', 'year 2016']], on='Institution', how='outer')
persist = persist.rename(columns={'year 2014': 'persist 2014', 'year 2015': 'persist 2015', 'year 2016': 'persist 2016'})

# Join fall_pivot and persist on Institution
df = fall_pivot.merge(persist, on='Institution', how='outer')

# Join cohort data s4 on Institution
df = df.merge(s4, on='Institution', how='outer')

# Convert types to match target schema
for col in ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

for col in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df = df[['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)', 'persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)