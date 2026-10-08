import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_81/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_81/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_81/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_81/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Define aggregation functions
def agg_categories(series):
    # Combine unique categories values into a sorted list string
    # The categories column can be int or list-like string, so parse carefully
    import ast

    unique_vals = set()
    for val in series.dropna():
        # val can be int, float, or string representing list or int
        if isinstance(val, str):
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, list):
                    unique_vals.update(parsed)
                else:
                    unique_vals.add(parsed)
            except:
                # If parsing fails, add as is
                unique_vals.add(val)
        else:
            unique_vals.add(val)
    # Sort and convert to list string
    unique_list = sorted(unique_vals, key=lambda x: (str(type(x)), x))
    return str(unique_list)

# For other columns, take first non-null value
agg_dict = {
    'categories': agg_categories,
    'commentCount': 'first',
    'completed': 'first',
    'copyright': 'first',
    'cover': 'first',
    'cover_timestamp': 'first',
    'createDate': 'first',
    'deleted': 'first',
    'description': 'first',
    'firstPartId': 'first',
    'firstPublishedPart.createDate': 'first',
    'firstPublishedPart.id': 'first',
    'language.id': 'first',
    'language.name': 'first',
    'lastPublishedPart.createDate': 'first',
    'lastPublishedPart.id': 'first',
    'length': 'first',
    'mature': 'first',
    'modifyDate': 'first',
    'numParts': 'first',
    'parts': 'first',
    'rating': 'first',
    'readCount': 'first',
    'tags': 'first',
    'title': 'first',
    'url': 'first',
    'user.avatar': 'first',
    'user.fullname': 'first',
    'user.name': 'first',
    'voteCount': 'first'
}

df_grouped = df.groupby('id', as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_columns = ['categories', 'commentCount', 'completed', 'copyright', 'cover', 'cover_timestamp', 'createDate', 'deleted', 'description', 'firstPartId', 'firstPublishedPart.createDate', 'firstPublishedPart.id', 'id', 'language.id', 'language.name', 'lastPublishedPart.createDate', 'lastPublishedPart.id', 'length', 'mature', 'modifyDate', 'numParts', 'parts', 'rating', 'readCount', 'tags', 'title', 'url', 'user.avatar', 'user.fullname', 'user.name', 'voteCount']

df_grouped = df_grouped[target_columns]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_81/target_multisource_mcts.csv", index=False)