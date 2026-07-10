import pandas as pd
import re

def extract_year(year_str):
    match = re.match(r"(\d{4})", str(year_str))
    if match:
        return int(match.group(1))
    return None

def winner_to_int(winner_str):
    return 1 if str(winner_str).strip().upper() == "YES" else 0

def category_to_int(cat_series):
    unique_cats = cat_series.dropna().unique()
    cat_map = {cat: i+1 for i, cat in enumerate(sorted(unique_cats))}
    return cat_series.map(cat_map)

def movie_to_int(movie_series):
    unique_movies = movie_series.dropna().unique()
    movie_map = {movie: i+1 for i, movie in enumerate(sorted(unique_movies))}
    return movie_series.map(movie_map)

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Year'] = df['Year'].apply(extract_year)

df['Winner'] = df['Winner'].apply(winner_to_int)

df['Category'] = category_to_int(df['Category'])

df['Movie'] = movie_to_int(df['Movie'])

# Group by Nominee and Year, aggregate Category and Movie by first, Winner by sum
agg_df = df.groupby(['Nominee', 'Year'], as_index=False).agg({
    'Category': 'first',
    'Movie': 'first',
    'Winner': 'sum'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)