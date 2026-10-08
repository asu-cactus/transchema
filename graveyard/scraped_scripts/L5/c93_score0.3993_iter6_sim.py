import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv", index_col=0)

join_cols = ['Year', 'Category']
joined = pd.merge(s3, s4, on=join_cols, suffixes=('_3', '_4'))

def unify_columns(df, suffix):
    df = df.copy()
    df['Nominee'] = df['Nominee' + suffix].astype(str)
    df['Movie'] = df['Movie' + suffix].astype(str)
    df['Winner'] = df['Winner' + suffix].astype(str)
    return df[['Year', 'Category', 'Nominee', 'Movie', 'Winner']]

joined_3 = unify_columns(joined, '_3')
joined_4 = unify_columns(joined, '_4')

joined_combined = pd.concat([joined_3, joined_4], ignore_index=True)

all_sources = pd.concat([s0, s1, s2, joined_combined], ignore_index=True)

def clean_year(y):
    if isinstance(y, str):
        y = y.split(' ')[0]
    try:
        return int(y)
    except:
        return pd.NA

all_sources['Year'] = all_sources['Year'].map(clean_year).astype('Int64')

all_sources['Category'] = all_sources['Category'].astype(str)
all_sources['Nominee'] = all_sources['Nominee'].astype(str)
all_sources['Movie'] = all_sources['Movie'].astype(str)

def winner_to_int(w):
    if isinstance(w, str) and w.strip().upper() == 'YES':
        return 1
    try:
        return int(w)
    except:
        return 0

all_sources['Winner'] = all_sources['Winner'].map(winner_to_int).astype('Int64')

all_sources['Nominee'] = all_sources['Nominee'].apply(lambda x: 1 if x.strip() != '' else 0).astype('Int64')
all_sources['Movie'] = all_sources['Movie'].apply(lambda x: 1 if x.strip() != '' else 0).astype('Int64')

result = all_sources[['Category', 'Year', 'Nominee', 'Movie', 'Winner']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)