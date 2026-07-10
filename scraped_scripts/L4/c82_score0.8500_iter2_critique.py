import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Step 1: UNION Source0, Source1, Source3 after unpivoting year columns to a common schema
def unpivot_persist(df, year_col_name):
    # df has columns: Institution, year XXXX
    # Rename year column to 'year' and persist count column to 'persist'
    df_renamed = df.rename(columns={year_col_name: 'persist'})
    df_renamed['year'] = int(year_col_name.split()[-1])  # extract year as int
    return df_renamed[['Institution', 'year', 'persist']]

persist0 = unpivot_persist(s0, 'year 2016')
persist1 = unpivot_persist(s1, 'year 2014')
persist3 = unpivot_persist(s3, 'year 2015')

persist_union = pd.concat([persist0, persist1, persist3], ignore_index=True)

# Pivot to get columns persist 2014, persist 2015, persist 2016
persist_pivot = persist_union.pivot(index='Institution', columns='year', values='persist').reset_index()
persist_pivot = persist_pivot.rename(columns={
    2014: 'persist 2014',
    2015: 'persist 2015',
    2016: 'persist 2016'
})

# Step 2: Join Source2 and Source4 on Institution
df_dim = pd.merge(s2, s4, on='Institution', how='inner')

# Step 3: Join the pivoted persistence table with the dimension table on Institution
df = pd.merge(df_dim, persist_pivot, on='Institution', how='inner')

# Step 4: Group by Institution to ensure uniqueness (no aggregation needed as data is unique per Institution)
df = df.groupby('Institution', as_index=False).first()

# Step 5: Select and reorder columns as per target schema
df = df[[
    'Institution',
    '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)',
    'persist 2014', 'persist 2015', 'persist 2016',
    'Cohort 2014', 'Cohort 2015', 'Cohort 2016'
]]

# Step 6: Cast integer columns to Int64 (nullable integer)
for col in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    df[col] = df[col].astype('Int64')

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)