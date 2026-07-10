import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_82/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Define aggregation functions per column
agg_funcs = {
    'categories': 'first',
    'commentCount': 'sum',
    'completed': 'max',
    'copyright': 'sum',
    'cover': 'first',
    'cover_timestamp': 'first',
    'createDate': 'first',
    'deleted': 'max',
    'description': 'first',
    'firstPartId': 'first',
    'firstPublishedPart.createDate': 'first',
    'firstPublishedPart.id': 'first',
    'language.id': 'first',
    'language.name': 'first',
    'lastPublishedPart.createDate': 'first',
    'lastPublishedPart.id': 'first',
    'length': 'sum',
    'mature': 'max',
    'modifyDate': 'first',
    'numParts': 'sum',
    'parts': 'first',
    'rating': 'sum',
    'readCount': 'sum',
    'tags': 'first',
    'title': 'first',
    'url': 'first',
    'user.avatar': 'first',
    'user.fullname': 'first',
    'user.name': 'first',
    'voteCount': 'sum'
}

# Group by 'id' and aggregate
df_final = df.groupby('id', as_index=False).agg(agg_funcs)

# Reorder columns to match target schema exactly
target_columns = ['categories', 'commentCount', 'completed', 'copyright', 'cover', 'cover_timestamp', 'createDate', 'deleted', 'description', 'firstPartId', 'firstPublishedPart.createDate', 'firstPublishedPart.id', 'id', 'language.id', 'language.name', 'lastPublishedPart.createDate', 'lastPublishedPart.id', 'length', 'mature', 'modifyDate', 'numParts', 'parts', 'rating', 'readCount', 'tags', 'title', 'url', 'user.avatar', 'user.fullname', 'user.name', 'voteCount']

df_final = df_final[target_columns]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_82/target_multisource_mcts.csv", index=False)