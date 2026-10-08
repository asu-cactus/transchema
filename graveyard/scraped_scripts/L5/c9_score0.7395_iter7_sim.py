import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

def clean_year(y):
    if isinstance(y, str):
        # Extract the first 4-digit year from the string
        import re
        m = re.search(r'\d{4}', y)
        if m:
            return int(m.group(0))
    return pd.NA

df_all['Year'] = df_all['Year'].apply(clean_year)

def clean_category(cat):
    if isinstance(cat, str):
        # Map categories to integers by factorizing
        return cat
    return pd.NA

df_all['Category'] = df_all['Category'].astype(str)

df_all['Winner'] = df_all['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

df_all['Nominee'] = df_all['Nominee'].astype(str)
df_all['Movie'] = df_all['Movie'].astype(str)

grouped = df_all.groupby(['Nominee', 'Year', 'Category', 'Movie', 'Winner'], dropna=False).size().reset_index(name='Winner_count')

# According to target schema, 'Winner' is integer, so we replace 'Winner' column by the count of Winner occurrences
# But target examples show Winner as 1 or 0, so we keep Winner as is and ignore count? 
# The partial plan says COUNT(Source5_9_0.Winner), so we keep count as Winner column.

# Rename columns to target schema
result = grouped.rename(columns={'Winner_count': 'Winner'})

# Convert Category and Movie to integer by factorizing (assign integer codes)
result['Category'] = pd.factorize(result['Category'])[0] + 1
result['Movie'] = pd.factorize(result['Movie'])[0] + 1

result = result[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)