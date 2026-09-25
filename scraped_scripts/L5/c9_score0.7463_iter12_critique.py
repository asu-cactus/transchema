import pandas as pd

# Read all source files
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

# Select relevant columns to ensure consistent schema
dfs = [df0, df1, df2, df3, df4]
dfs = [df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']] for df in dfs]

# UNION all source tables
union_all = pd.concat(dfs, ignore_index=True)

# GROUP BY Nominee, Year, Category and aggregate Movie and Winner by max
result = union_all.groupby(['Nominee', 'Year', 'Category'], as_index=False).agg({'Movie': 'max', 'Winner': 'max'})

# Ensure types match target schema
result['Nominee'] = result['Nominee'].astype(str)
result['Year'] = result['Year'].astype('Int64')
result['Category'] = result['Category'].astype('Int64')
result['Movie'] = result['Movie'].astype('Int64')
result['Winner'] = result['Winner'].astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)