import pandas as pd
import ast

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

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    if 'hashtags' in df.columns:
        def parse_hashtags(x):
            if pd.isna(x):
                return []
            if isinstance(x, list):
                return x
            if isinstance(x, str):
                x = x.strip()
                if x == '[]':
                    return []
                try:
                    parsed = ast.literal_eval(x)
                    if isinstance(parsed, list):
                        # parsed is list of dicts or empty list
                        if all(isinstance(i, dict) and 'text' in i for i in parsed):
                            return [i['text'] for i in parsed]
                        else:
                            return parsed
                    else:
                        return []
                except:
                    return []
            return []
        df['hashtags'] = df['hashtags'].apply(parse_hashtags)
        df['hashtags'] = df['hashtags'].apply(lambda x: str(x) if isinstance(x, list) else '[]')
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_all = df_all[['created_at', 'text', 'coordinates', 'hashtags']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_16/target_multisource_mcts.csv", index=False)