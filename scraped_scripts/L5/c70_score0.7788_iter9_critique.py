import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Nominee'] = df['Nominee'].astype(str)

def extract_year_int(year_str):
    if pd.isna(year_str):
        return None
    m = re.search(r'\d{4}', year_str)
    if m:
        return int(m.group(0))
    return None

df['Year'] = df['Year'].map(extract_year_int)

def category_to_int(cat_series):
    unique_cats = cat_series.dropna().unique()
    cat_map = {cat: i+1 for i, cat in enumerate(sorted(unique_cats))}
    return cat_series.map(cat_map), cat_map

df['Category'], category_map = category_to_int(df['Category'])

def movie_to_int(movie_series):
    unique_movies = movie_series.dropna().unique()
    movie_map = {movie: i+1 for i, movie in enumerate(sorted(unique_movies))}
    return movie_series.map(movie_map), movie_map

df['Movie'], movie_map = movie_to_int(df['Movie'])

def winner_to_int(winner_series):
    return winner_series.str.upper().map({'YES':1, 'NO':0}).fillna(0).astype(int)

df['Winner'] = winner_to_int(df['Winner'])

# Group by Nominee, Year, Category, Movie and aggregate Winner by sum
df = df.groupby(['Nominee', 'Year', 'Category', 'Movie'], as_index=False).agg({'Winner':'sum'})

# Since Winner is binary, sum will be 1 or more; convert to 1 (presence)
df['Winner'] = (df['Winner'] > 0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_70/target_multisource_mcts.csv", index=False)