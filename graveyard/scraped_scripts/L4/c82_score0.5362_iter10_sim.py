import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

def unpivot_year(df, year_col):
    df_unpivot = df.melt(id_vars=['Institution'], var_name='year', value_name='value')
    if year_col:
        # For these sources, year is in column name, so convert to uniform year string
        df_unpivot['year'] = df_unpivot['year'].astype(str).str.extract(r'(\d{4})')[0]
    else:
        # For s2, no unpivot needed here
        pass
    return df_unpivot

# Unpivot s0, s1, s3 which have schema ['Institution', 'year XXXX']
# For s0, s1, s3, the year column is the second column, named e.g. 'year 2016'
# We convert them to a uniform format: year as string of the year number
s0_unpivot = s0.rename(columns={s0.columns[1]: 'year'}).copy()
s0_unpivot['year'] = s0_unpivot['year'].astype(str)
s0_unpivot = s0_unpivot.rename(columns={'year': 'year', s0.columns[1]: 'value'})
s0_unpivot = s0_unpivot.rename(columns={s0.columns[1]: 'value'})  # redundant but safe
s0_unpivot = s0.melt(id_vars=['Institution'], var_name='year', value_name='value')
s0_unpivot['year'] = s0_unpivot['year'].str.extract(r'(\d{4})')[0]

s1_unpivot = s1.melt(id_vars=['Institution'], var_name='year', value_name='value')
s1_unpivot['year'] = s1_unpivot['year'].str.extract(r'(\d{4})')[0]

s3_unpivot = s3.melt(id_vars=['Institution'], var_name='year', value_name='value')
s3_unpivot['year'] = s3_unpivot['year'].str.extract(r'(\d{4})')[0]

unpivoted_0_1_3 = pd.concat([s0_unpivot, s1_unpivot, s3_unpivot], ignore_index=True)

# s2 has columns: Institution, (Fall 2000), ..., (Fall 2014)
# We want to join s2 with unpivoted_0_1_3 on Institution and year
# First, melt s2 for (Fall 2011) to (Fall 2014) only, since target only needs those years from s2
fall_cols = ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']
s2_fall = s2[['Institution'] + fall_cols].copy()
s2_melt = s2_fall.melt(id_vars=['Institution'], var_name='year', value_name='value')
s2_melt['year'] = s2_melt['year'].str.extract(r'(\d{4})')[0]

# Join unpivoted_0_1_3 and s2_melt on Institution and year
joined_0_2 = pd.merge(unpivoted_0_1_3, s2_melt, on=['Institution', 'year'], how='outer', suffixes=('_persist', '_fall'))

# We want to create columns for persist years and fall years separately
# persist years are from unpivoted_0_1_3 (years 2014, 2015, 2016)
# fall years are from s2 (2011-2014)
# So separate these values accordingly

# Create a dataframe with Institution, year, persist_value, fall_value
joined_0_2['persist_value'] = joined_0_2['value_persist']
joined_0_2['fall_value'] = joined_0_2['value_fall']

# Pivot persist_value for years 2014, 2015, 2016
persist_df = joined_0_2[joined_0_2['year'].isin(['2014','2015','2016'])][['Institution','year','persist_value']].dropna(subset=['persist_value'])
persist_pivot = persist_df.pivot(index='Institution', columns='year', values='persist_value')
persist_pivot.columns = ['persist ' + col for col in persist_pivot.columns]

# Pivot fall_value for years 2011-2014
fall_df = joined_0_2[joined_0_2['year'].isin(['2011','2012','2013','2014'])][['Institution','year','fall_value']].dropna(subset=['fall_value'])
fall_pivot = fall_df.pivot(index='Institution', columns='year', values='fall_value')
fall_pivot.columns = ['(Fall ' + col + ')' for col in fall_pivot.columns]

# Combine fall_pivot and persist_pivot
combined = pd.concat([fall_pivot, persist_pivot], axis=1)

# Join combined with s4 on Institution
s4.set_index('Institution', inplace=True)
final = combined.join(s4, how='outer')

# persist 2014 is from s1 (year 2014) unpivoted, but we already have persist 2014 in persist_pivot
# However, s1 only has year 2014, so persist 2014 is from persist_pivot['persist 2014']
# But target schema has persist 2014 as integer, so convert accordingly
final['persist 2014'] = final['persist 2014'].fillna(0).astype(int)
final['persist 2015'] = final['persist 2015'].fillna(0).astype(int)
final['persist 2016'] = final['persist 2016'].fillna(0).astype(int)

# Cohort columns are already in s4, convert to int
for c in ['Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    if c in final.columns:
        final[c] = final[c].fillna(0).astype(int)

# Ensure fall columns are float
for c in ['(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)']:
    if c in final.columns:
        final[c] = final[c].astype(float)

final.reset_index(inplace=True)

# Select and order columns as target schema
cols = ['Institution', '(Fall 2011)', '(Fall 2012)', '(Fall 2013)', '(Fall 2014)', 'persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']
final = final[cols]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)