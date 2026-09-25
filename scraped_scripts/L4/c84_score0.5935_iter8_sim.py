import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

# Clean each df: drop rows where 'age_grp' is not a valid age group (remove header-like rows)
def clean_df(df):
    return df[df['age_grp'].str.contains(r'^\d+-?\d*$', na=False)]

df0 = clean_df(df0)
df1 = clean_df(df1)
df2 = clean_df(df2)
df3 = clean_df(df3)
df4 = clean_df(df4)

# Rename columns to avoid overlap except 'age_grp'
# We keep the columns from df0 as is, rename others with suffixes
df1_ren = df1.rename(columns=lambda c: c if c == 'age_grp' else c + '_1')
df2_ren = df2.rename(columns=lambda c: c if c == 'age_grp' else c + '_2')
df3_ren = df3.rename(columns=lambda c: c if c == 'age_grp' else c + '_3')
df4_ren = df4.rename(columns=lambda c: c if c == 'age_grp' else c + '_4')

# Merge all on 'age_grp'
df_merged = df0.merge(df1_ren, on='age_grp', how='outer') \
               .merge(df2_ren, on='age_grp', how='outer') \
               .merge(df3_ren, on='age_grp', how='outer') \
               .merge(df4_ren, on='age_grp', how='outer')

# Now we want to pivot the merged data so that each source's data becomes rows with columns: age_grp, Count, Notes, Rate, Statistics
# We have columns:
# From df0: Count, Notes, Rate, Statistics
# From df1: Count_1, Notes_1, Rate_1, Statistics_1
# ...
# We will melt these columns into rows, stacking the data vertically.

# Prepare list of source suffixes and their columns
sources = [
    ('', ['Count', 'Notes', 'Rate', 'Statistics']),
    ('_1', ['Count_1', 'Notes_1', 'Rate_1', 'Statistics_1']),
    ('_2', ['Count_2', 'Notes_2', 'Rate_2', 'Statistics_2']),
    ('_3', ['Count_3', 'Notes_3', 'Rate_3', 'Statistics_3']),
    ('_4', ['Count_4', 'Notes_4', 'Rate_4', 'Statistics_4']),
]

dfs = []
for suffix, cols in sources:
    sub_df = df_merged[['age_grp'] + cols].copy()
    sub_df.columns = ['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']
    dfs.append(sub_df)

result = pd.concat(dfs, ignore_index=True)

# Convert Count and Rate to float (they may already be, but ensure)
result['Count'] = pd.to_numeric(result['Count'], errors='coerce')
result['Rate'] = pd.to_numeric(result['Rate'], errors='coerce')

# Ensure Notes and Statistics are strings or NaN
result['Notes'] = result['Notes'].astype('string')
result['Statistics'] = result['Statistics'].astype('string')

# Sort by age_grp and Count descending (optional, not required)
result = result.sort_values(by=['age_grp', 'Count'], ascending=[True, False])

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)