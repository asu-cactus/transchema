import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

def clean_year(y):
    if pd.isna(y):
        return None
    y = str(y)
    # Extract the first 4-digit year from the string
    import re
    m = re.search(r"\b(\d{4})\b", y)
    if m:
        return int(m.group(1))
    # fallback: try to convert directly
    try:
        return int(y)
    except:
        return None

df['Year'] = df['Year'].map(clean_year)

def clean_category(cat):
    if pd.isna(cat):
        return None
    cat = str(cat)
    # Map categories to integers by factorizing
    return cat

df['Category'] = df['Category'].astype(str)
df['Nominee'] = df['Nominee'].astype(str)
df['Movie'] = df['Movie'].astype(str)
df['Winner'] = df['Winner'].astype(str)

# Factorize Category to integer codes starting from 1
df['Category'] = pd.factorize(df['Category'])[0] + 1

# Factorize Movie to integer codes starting from 1
df['Movie'] = pd.factorize(df['Movie'])[0] + 1

# Winner: map 'YES' to 1, else 0
df['Winner'] = df['Winner'].str.upper().map(lambda x: 1 if x == 'YES' else 0)

# Ensure Nominee is string (already done)
# Year is int (cleaned)
df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)