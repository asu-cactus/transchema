import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_16/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_8.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['created_at'] = df['created_at'].astype(str)
df['text'] = df['text'].astype(str)
df['coordinates'] = df['coordinates'].astype(str)
# Convert hashtags column to string representation of list of hashtag texts
def hashtags_to_str(h):
    if pd.isna(h):
        return '[]'
    if isinstance(h, str):
        try:
            import ast
            parsed = ast.literal_eval(h)
            if isinstance(parsed, list):
                texts = []
                for item in parsed:
                    if isinstance(item, dict) and 'text' in item:
                        texts.append(item['text'])
                    elif isinstance(item, str):
                        texts.append(item)
                return str(texts)
            else:
                return '[]'
        except:
            return '[]'
    if isinstance(h, list):
        texts = []
        for item in h:
            if isinstance(item, dict) and 'text' in item:
                texts.append(item['text'])
            elif isinstance(item, str):
                texts.append(item)
        return str(texts)
    return '[]'

df['hashtags'] = df['hashtags'].apply(hashtags_to_str)

df = df[['created_at', 'text', 'coordinates', 'hashtags']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_16/target_multisource_mcts.csv", index=False)