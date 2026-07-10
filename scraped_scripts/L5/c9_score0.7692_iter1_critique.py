import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

def extract_year(x):
    m = re.match(r"(\d{4})", str(x))
    return int(m.group(1)) if m else None

def category_to_int(cat):
    if not hasattr(category_to_int, "mapping"):
        unique_cats = sorted(df['Category'].dropna().unique())
        category_to_int.mapping = {c: i+1 for i, c in enumerate(unique_cats)}
    return category_to_int.mapping.get(cat, None)

def movie_to_int(movie):
    if not hasattr(movie_to_int, "mapping"):
        movies = df['Movie'].dropna().apply(lambda x: re.sub(r"\s*\{.*\}", "", str(x))).unique()
        movie_to_int.mapping = {m: i+1 for i, m in enumerate(sorted(movies))}
    clean_movie = re.sub(r"\s*\{.*\}", "", str(movie))
    return movie_to_int.mapping.get(clean_movie, None)

def winner_to_int(w):
    w = str(w).strip().upper()
    return 1 if w == "YES" else 0

df['Year'] = df['Year'].map(extract_year)
df['Category'] = df['Category'].map(category_to_int)
df['Movie'] = df['Movie'].map(movie_to_int)
df['Winner'] = df['Winner'].map(winner_to_int)
df['Nominee'] = df['Nominee'].astype(str)

df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

# Group by Nominee, Year, Category, Movie and aggregate Winner by max to remove duplicates and keep winner info
df = df.groupby(['Nominee', 'Year', 'Category', 'Movie'], as_index=False).agg({'Winner': 'max'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)