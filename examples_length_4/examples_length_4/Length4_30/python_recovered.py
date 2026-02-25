import pandas as pd

def load_and_prepare_source(path):
    # load CSV with ignoring the first index column
    df = pd.read_csv(path, index_col=0)
    
    # Ensure data types conformity as per target schema:
    # The source columns already have correct names and types based on examples, just ensure correct types:
    # categories: string (convert any list to string), commentCount: int, completed: bool, copyright: int,
    # cover: string, cover_timestamp: string, createDate: string, deleted: bool, description: string or NaN,
    # firstPartId: int, firstPublishedPart.createDate: string, firstPublishedPart.id: int,
    # id: int, language.id: int, language.name: string,
    # lastPublishedPart.createDate: string, lastPublishedPart.id: int,
    # length: int, mature: bool, modifyDate: string,
    # numParts: int, parts: string (JSON-string), rating: int,
    # readCount: int, tags: string (list-string), title: string,
    # url: string, user.avatar: string, user.fullname: string or NaN,
    # user.name: string, voteCount: int
    
    # categories: some are integers, some may be lists -> convert all to string
    df['categories'] = df['categories'].apply(lambda x: x if isinstance(x, str) else str(x))
    
    # commentCount, copyright, firstPartId, firstPublishedPart.id, id, language.id, lastPublishedPart.id,
    # length, numParts, rating, readCount, voteCount forced to int
    int_cols = [
        'commentCount', 'copyright', 'firstPartId', 'firstPublishedPart.id', 'id',
        'language.id', 'lastPublishedPart.id', 'length', 'numParts', 'rating', 'readCount', 'voteCount'
    ]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Booleans: completed, deleted, mature
    bool_cols = ['completed', 'deleted', 'mature']
    for col in bool_cols:
        # Some may be already boolean, some may be string or int -> convert to bool
        df[col] = df[col].astype(bool)
    
    # description, user.fullname can have NaN; replace NaN to None equivalent for string columns
    str_nullable_cols = ['description', 'user.fullname']
    for col in str_nullable_cols:
        df[col] = df[col].where(pd.notnull(df[col]), None)
    
    # 'parts' and 'tags' columns: confirm as string; if lists, convert to string
    df['parts'] = df['parts'].apply(lambda x: x if isinstance(x, str) else str(x))
    df['tags'] = df['tags'].apply(lambda x: x if isinstance(x, str) else str(x))
    
    # The rest columns are strings and can be used as is:
    # cover, cover_timestamp, createDate, firstPublishedPart.createDate, language.name,
    # lastPublishedPart.createDate, modifyDate, title, url, user.avatar, user.name
    
    # For safety convert these columns explicitly to string (and fill NaN with empty string if any)
    str_cols = [
        'cover', 'cover_timestamp', 'createDate', 'firstPublishedPart.createDate',
        'language.name', 'lastPublishedPart.createDate', 'modifyDate', 'title',
        'url', 'user.avatar', 'user.name'
    ]
    for col in str_cols:
        df[col] = df[col].astype(str)
    
    return df

def main():
    # Source file paths
    source_files = [
        'autopipeline-benchmarks/github-pipelines/length4_30/test_0.csv',
        'autopipeline-benchmarks/github-pipelines/length4_30/test_1.csv',
        'autopipeline-benchmarks/github-pipelines/length4_30/test_2.csv',
        'autopipeline-benchmarks/github-pipelines/length4_30/test_3.csv',
        'autopipeline-benchmarks/github-pipelines/length4_30/test_4.csv'
    ]
    
    # Load each source table, prepare and store in list
    dfs = []
    for path in source_files:
        df = load_and_prepare_source(path)
        dfs.append(df)
    
    # All source tables share the same schema and same target schema, 
    # so union (concat) all rows is the appropriate operation to match the target table.
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Ensure final column order as target schema:
    target_columns = [
        'categories', 'commentCount', 'completed', 'copyright', 'cover', 'cover_timestamp', 'createDate',
        'deleted', 'description', 'firstPartId', 'firstPublishedPart.createDate', 'firstPublishedPart.id',
        'id', 'language.id', 'language.name', 'lastPublishedPart.createDate', 'lastPublishedPart.id',
        'length', 'mature', 'modifyDate', 'numParts', 'parts', 'rating', 'readCount', 'tags', 'title',
        'url', 'user.avatar', 'user.fullname', 'user.name', 'voteCount'
    ]

    # Some source data may contain extra columns or maybe missing some, so enforce exact columns & order:
    missing_cols = [c for c in target_columns if c not in merged_df.columns]
    if missing_cols:
        # If missing columns (unlikely), create them with default None or appropriate type
        for c in missing_cols:
            merged_df[c] = None
    
    merged_df = merged_df[target_columns]

    # Write final result to output CSV
    merged_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_30/target_multisource_cot.csv', index=False)


if __name__ == '__main__':
    main()