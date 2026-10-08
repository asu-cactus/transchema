import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

join_0_1 = pd.merge(df0, df1, on=['title', 'company', 'location'], suffixes=('_0', '_1'))
join_0_1_2 = pd.merge(join_0_1, df2, on=['title', 'company', 'location'])
join_0_1_2_3 = pd.merge(join_0_1_2, df3, on=['title', 'company', 'location'], suffixes=('', '_3'))

# After joins, columns are duplicated with suffixes; we need to pivot these columns to match target schema:
# Target columns: location (string), title (int), company (int), summary (int), salary (int), href (int), rate (int), reviews (int), org_salary_period (int)
# The target examples show these columns as integers (likely counts or indicators).
# We will create a pivoted table where for each location, the count of each attribute occurrence from each source is 1 if present.

# Extract columns for pivoting from each source suffix
def to_indicator(df, suffix):
    cols = ['title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
    indicators = {}
    for c in cols:
        col_name = c + suffix if suffix else c
        if col_name in df.columns:
            # Convert non-null to 1, null to 0
            indicators[c + suffix] = df[col_name].notnull().astype(int)
        else:
            indicators[c + suffix] = pd.Series(0, index=df.index)
    return pd.DataFrame(indicators)

ind_0 = to_indicator(df0, '')
ind_1 = to_indicator(df1, '_1')
ind_2 = to_indicator(df2, '')
ind_3 = to_indicator(df3, '')

# For join_0_1, columns from df0 have no suffix, from df1 have _1 suffix
ind_join_0_1 = to_indicator(join_0_1, '_0').add(to_indicator(join_0_1, '_1'), fill_value=0)

# But since we merged join_0_1 with df2 and df3, let's build indicators from join_0_1_2_3 directly:
# The final merged df has columns from all sources, some with suffixes _0, _1, _3 or none.
# We'll create indicator columns for each attribute from each source, then sum them per location.

# For clarity, create indicator columns for each source in the final merged df:
def indicator_from_merged(df, suffix):
    cols = ['title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
    ind = pd.DataFrame()
    for c in cols:
        col_name = c + suffix if suffix else c
        if col_name in df.columns:
            ind[c + suffix] = df[col_name].notnull().astype(int)
        else:
            ind[c + suffix] = 0
    return ind

ind_0 = indicator_from_merged(join_0_1_2_3, '_0')
ind_1 = indicator_from_merged(join_0_1_2_3, '_1')
ind_2 = indicator_from_merged(join_0_1_2_3, '')
ind_3 = indicator_from_merged(join_0_1_2_3, '_3')

# Sum indicators per location for each attribute across sources
location = join_0_1_2_3['location']

df_indicators = pd.DataFrame({'location': location})
for attr in ['title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']:
    df_indicators[attr] = (
        ind_0[attr + '_0'].fillna(0).astype(int) +
        ind_1[attr + '_1'].fillna(0).astype(int) +
        ind_2[attr].fillna(0).astype(int) +
        ind_3[attr + '_3'].fillna(0).astype(int)
    )

# Group by location and sum to aggregate counts
result = df_indicators.groupby('location').sum().reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)