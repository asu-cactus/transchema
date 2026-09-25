import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv", index_col=0)

# Normalize Year column: extract the year number as integer from strings like "2010 (83rd)"
def extract_year(y):
    try:
        return int(y.split()[0])
    except:
        return pd.NA

for df in [df0, df1, df2, df3, df4]:
    df['Year'] = df['Year'].map(extract_year)
    # Normalize Category to integer by factorizing (assign unique int per category)
    df['Category'] = pd.factorize(df['Category'])[0] + 1
    # Normalize Winner to integer: 'YES' -> 1, else 0
    df['Winner'] = df['Winner'].apply(lambda x: 1 if str(x).strip().upper() == 'YES' else 0)
    # Normalize Movie to integer by factorizing (unique int per movie)
    df['Movie'] = pd.factorize(df['Movie'])[0] + 1
    # Nominee as string, strip spaces
    df['Nominee'] = df['Nominee'].astype(str).str.strip()

# Join df0 and df1 on Year, Category, Nominee (inner join)
joined_0_1 = pd.merge(df0, df1, on=['Year', 'Category', 'Nominee'], suffixes=('_0', '_1'))

# After join, we have columns:
# Year, Category, Nominee, Movie_0, Winner_0, Movie_1, Winner_1
# We want to combine Movie and Winner columns from both sources into one set of columns.
# Since Movie and Winner are integers, we can take max to indicate presence.
joined_0_1['Movie'] = joined_0_1[['Movie_0', 'Movie_1']].max(axis=1)
joined_0_1['Winner'] = joined_0_1[['Winner_0', 'Winner_1']].max(axis=1)
joined_0_1 = joined_0_1[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

# Union the joined_0_1 with df2, df3, df4 (all have same schema)
df2 = df2[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]
df3 = df3[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]
df4 = df4[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

union_all = pd.concat([joined_0_1, df2, df3, df4], ignore_index=True)

# Group by Nominee, Year, Category, aggregate Movie and Winner by max (to keep presence)
result = union_all.groupby(['Nominee', 'Year', 'Category'], as_index=False).agg({'Movie':'max', 'Winner':'max'})

# Ensure types match target schema
result['Nominee'] = result['Nominee'].astype(str)
result['Year'] = result['Year'].astype('Int64')
result['Category'] = result['Category'].astype('Int64')
result['Movie'] = result['Movie'].astype('Int64')
result['Winner'] = result['Winner'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)