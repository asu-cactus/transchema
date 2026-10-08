import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_80/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_80/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_80/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_80/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

group_key = ['id']

sum_cols = ['commentCount', 'readCount', 'voteCount', 'numParts', 'length']
max_cols = ['completed', 'copyright', 'deleted', 'mature', 'rating']
first_cols = [col for col in df.columns if col not in group_key + sum_cols + max_cols]

agg_dict = {col: 'sum' for col in sum_cols}
agg_dict.update({col: 'max' for col in max_cols})
agg_dict.update({col: 'first' for col in first_cols})

df_grouped = df.groupby(group_key, as_index=False).agg(agg_dict)

target_columns = ['categories', 'commentCount', 'completed', 'copyright', 'cover', 'cover_timestamp', 'createDate', 'deleted', 'description', 'firstPartId', 'firstPublishedPart.createDate', 'firstPublishedPart.id', 'id', 'language.id', 'language.name', 'lastPublishedPart.createDate', 'lastPublishedPart.id', 'length', 'mature', 'modifyDate', 'numParts', 'parts', 'rating', 'readCount', 'tags', 'title', 'url', 'user.avatar', 'user.fullname', 'user.name', 'voteCount']

df_grouped = df_grouped[target_columns]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_80/target_multisource_mcts.csv", index=False)