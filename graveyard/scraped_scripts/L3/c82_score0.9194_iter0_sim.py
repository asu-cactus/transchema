import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_82/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_82/training_3.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Ensure columns have correct types matching target schema
bool_cols = ['completed', 'deleted', 'mature']
int_cols = ['commentCount', 'copyright', 'firstPartId', 'firstPublishedPart.id', 'id', 'language.id',
            'lastPublishedPart.id', 'length', 'numParts', 'rating', 'readCount', 'voteCount']
str_cols = ['categories', 'cover', 'cover_timestamp', 'createDate', 'description', 'firstPublishedPart.createDate',
            'language.name', 'lastPublishedPart.createDate', 'modifyDate', 'parts', 'tags', 'title', 'url',
            'user.avatar', 'user.fullname', 'user.name']

for c in bool_cols:
    if c in df.columns:
        df[c] = df[c].astype(bool)

for c in int_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)

for c in str_cols:
    if c in df.columns:
        df[c] = df[c].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_82/target_multisource_mcts.csv", index=False)