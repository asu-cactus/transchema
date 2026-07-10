import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv", index_col=0)

join_result = pd.merge(s3, s4, how='inner', on=['Year', 'Category'], suffixes=('_3', '_4'))

def to_int(val):
    try:
        return int(val)
    except:
        return 0

def winner_to_int(w):
    if isinstance(w, str) and w.strip().upper() == 'YES':
        return 1
    return 0

def nominee_to_int(n):
    if isinstance(n, str) and n.strip():
        return 1
    return 0

def movie_to_int(m):
    if isinstance(m, str) and m.strip():
        return 1
    return 0

def process_df(df):
    df = df.copy()
    df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
    df['Winner'] = df['Winner'].apply(winner_to_int)
    df['Nominee'] = df['Nominee'].apply(nominee_to_int)
    df['Movie'] = df['Movie'].apply(movie_to_int)
    df = df[['Category', 'Year', 'Nominee', 'Movie', 'Winner']]
    return df

s0p = process_df(s0)
s1p = process_df(s1)
s2p = process_df(s2)

j = join_result.copy()
j['Year'] = j['Year'].str.extract(r'(\d{4})').astype(int)
j['Winner_3'] = j['Winner_3'].apply(winner_to_int)
j['Winner_4'] = j['Winner_4'].apply(winner_to_int)
j['Nominee_3'] = j['Nominee_3'].apply(nominee_to_int)
j['Nominee_4'] = j['Nominee_4'].apply(nominee_to_int)
j['Movie_3'] = j['Movie_3'].apply(movie_to_int)
j['Movie_4'] = j['Movie_4'].apply(movie_to_int)
j['Nominee'] = j['Nominee_3'] + j['Nominee_4']
j['Movie'] = j['Movie_3'] + j['Movie_4']
j['Winner'] = j['Winner_3'] + j['Winner_4']
j = j[['Category', 'Year', 'Nominee', 'Movie', 'Winner']]

all_dfs = [s0p, s1p, s2p, j]
result = pd.concat(all_dfs, ignore_index=True)

result = result.groupby(['Category', 'Year'], as_index=False).sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)