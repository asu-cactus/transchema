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
    "autopipeline-benchmarks/github-pipelines/length9_16/training_8.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

def hashtags_to_str(h):
    if pd.isna(h):
        return "[]"
    if isinstance(h, list):
        return str(h)
    if isinstance(h, str):
        h = h.strip()
        if h == "[]":
            return "[]"
        try:
            parsed = ast.literal_eval(h)
            if isinstance(parsed, list):
                return str(parsed)
            else:
                return "[]"
        except:
            return "[]"
    return "[]"

df_all['hashtags'] = df_all['hashtags'].apply(hashtags_to_str)
df_all['created_at'] = df_all['created_at'].astype(str)
df_all['text'] = df_all['text'].astype(str)
df_all['coordinates'] = df_all['coordinates'].astype(str)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_16/target_multisource_mcts.csv", index=False)