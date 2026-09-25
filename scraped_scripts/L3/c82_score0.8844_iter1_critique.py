import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_82/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Define aggregation functions for each column
agg_funcs = {
    'categories': 'first',
    'commentCount': 'max',
    'completed': 'max',
    'copyright': 'max',
    'cover': 'first',
    'cover_timestamp': 'max',
    'createDate': 'max',
    'deleted': 'max',
    'description': 'first',
    'firstPartId': 'max',
    'firstPublishedPart.createDate': 'max',
    'firstPublishedPart.id': 'max',
    'id': 'max',  # grouping key, max or first is same
    'language.id': 'max',
    'language.name': 'first',
    'lastPublishedPart.createDate': 'max',
    'lastPublishedPart.id': 'max',
    'length': 'max',
    'mature': 'max',
    'modifyDate': 'max',
    'numParts': 'max',
    'parts': 'first',
    'rating': 'max',
    'readCount': 'max',
    'tags': 'first',
    'title': 'first',
    'url': 'first',
    'user.avatar': 'first',
    'user.fullname': 'first',
    'user.name': 'first',
    'voteCount': 'max'
}

# Group by 'id' and aggregate
df = df.groupby('id', as_index=False).agg(agg_funcs)

# Reorder columns to match target schema exactly
target_columns = ['categories', 'commentCount', 'completed', 'copyright', 'cover', 'cover_timestamp', 'createDate', 'deleted', 'description', 'firstPartId', 'firstPublishedPart.createDate', 'firstPublishedPart.id', 'id', 'language.id', 'language.name', 'lastPublishedPart.createDate', 'lastPublishedPart.id', 'length', 'mature', 'modifyDate', 'numParts', 'parts', 'rating', 'readCount', 'tags', 'title', 'url', 'user.avatar', 'user.fullname', 'user.name', 'voteCount']

df = df[target_columns]

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_82/target_multisource_mcts.csv", index=False)