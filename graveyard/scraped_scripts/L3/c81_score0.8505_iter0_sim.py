import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_81/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_81/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_81/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['categories'] = df['categories'].apply(lambda x: x if isinstance(x, str) else str(x) if pd.notnull(x) else x)

bool_cols = ['completed', 'deleted', 'mature']
for col in bool_cols:
    df[col] = df[col].astype(bool)

int_cols = ['commentCount', 'copyright', 'firstPartId', 'firstPublishedPart.id', 'id', 'language.id', 'lastPublishedPart.id', 'length', 'numParts', 'rating', 'readCount', 'voteCount']
for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

str_cols = ['cover', 'cover_timestamp', 'createDate', 'firstPublishedPart.createDate', 'language.name', 'lastPublishedPart.createDate', 'modifyDate', 'parts', 'tags', 'title', 'url', 'user.avatar', 'user.fullname', 'user.name', 'description']
for col in str_cols:
    df[col] = df[col].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_81/target_multisource_mcts.csv", index=False)