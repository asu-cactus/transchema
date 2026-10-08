import pandas as pd
import re

def extract_year(year_str):
    m = re.match(r"(\d{4})", year_str)
    if m:
        return int(m.group(1))
    return None

def category_to_int(cat_str):
    # Map each unique category string to a unique integer ID
    # We'll build a mapping dynamically
    return category_map.setdefault(cat_str, len(category_map) + 1)

def movie_to_int(movie_str):
    # Map each unique movie string to a unique integer ID
    return movie_map.setdefault(movie_str, len(movie_map) + 1)

def winner_to_int(winner_str):
    # Map 'YES' to 1, else 0
    return 1 if str(winner_str).strip().upper() == 'YES' else 0

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

category_map = {}
movie_map = {}

df['Year'] = df['Year'].map(extract_year)

df['Category'] = df['Category'].map(category_to_int)

df['Movie'] = df['Movie'].map(movie_to_int)

df['Winner'] = df['Winner'].map(winner_to_int)

df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

df['Year'] = df['Year'].astype('Int64')
df['Category'] = df['Category'].astype('Int64')
df['Movie'] = df['Movie'].astype('Int64')
df['Winner'] = df['Winner'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_70/target_multisource_mcts.csv", index=False)