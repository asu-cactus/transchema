import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_41/training_4.csv", index_col=0)

def clean_year(year_str):
    if pd.isna(year_str):
        return None
    # Extract the first 4 digit year from string like "2010 (83rd)"
    import re
    m = re.match(r"(\d{4})", year_str)
    if m:
        return int(m.group(1))
    return None

for df in [df0, df1, df2, df3, df4]:
    df['Year'] = df['Year'].map(clean_year)
    df['Category'] = df['Category'].astype(str).str.strip()
    df['Nominee'] = df['Nominee'].astype(str).str.strip()
    df['Movie'] = df['Movie'].astype(str).str.strip()
    df['Winner'] = df['Winner'].astype(str).str.strip()

# Join all 5 dataframes on all columns (Year, Category, Nominee, Movie, Winner)
# The join is done by merging pairwise on all columns, keeping only rows that appear in all sources
# Because the partial plan shows a JOIN on all columns, we do an inner join on all columns stepwise

# Start with df0
df_join = df0.copy()
for df in [df1, df2, df3, df4]:
    df_join = pd.merge(df_join, df, on=['Year','Category','Nominee','Movie','Winner'], how='inner')

# After join, group by Winner and aggregate counts of each column as integers
# Target schema: ['Winner': string, 'Year': integer, 'Category': integer, 'Nominee': integer, 'Movie': integer]
# The example shows counts per Winner for each column (Year, Category, Nominee, Movie)
# So count distinct values per Winner for each column

agg_df = df_join.groupby('Winner').agg({
    'Year': 'nunique',
    'Category': 'nunique',
    'Nominee': 'nunique',
    'Movie': 'nunique'
}).reset_index()

agg_df = agg_df.rename(columns={
    'Year': 'Year',
    'Category': 'Category',
    'Nominee': 'Nominee',
    'Movie': 'Movie',
    'Winner': 'Winner'
})

agg_df = agg_df.astype({
    'Year': 'int64',
    'Category': 'int64',
    'Nominee': 'int64',
    'Movie': 'int64',
    'Winner': 'string'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_41/target_multisource_mcts.csv", index=False)