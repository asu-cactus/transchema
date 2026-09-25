import pandas as pd

paths = {
    "Source9_6_0": "autopipeline-benchmarks/github-pipelines/length9_6/training_0.csv",
    "Source9_6_1": "autopipeline-benchmarks/github-pipelines/length9_6/training_1.csv",
    "Source9_6_2": "autopipeline-benchmarks/github-pipelines/length9_6/training_2.csv",
    "Source9_6_3": "autopipeline-benchmarks/github-pipelines/length9_6/training_3.csv",
    "Source9_6_4": "autopipeline-benchmarks/github-pipelines/length9_6/training_4.csv",
    "Source9_6_5": "autopipeline-benchmarks/github-pipelines/length9_6/training_5.csv",
    "Source9_6_6": "autopipeline-benchmarks/github-pipelines/length9_6/training_6.csv",
    "Source9_6_7": "autopipeline-benchmarks/github-pipelines/length9_6/training_7.csv",
    "Source9_6_8": "autopipeline-benchmarks/github-pipelines/length9_6/training_8.csv",
    "Source9_6_9": "autopipeline-benchmarks/github-pipelines/length9_6/training_9.csv",
    "Source9_6_10": "autopipeline-benchmarks/github-pipelines/length9_6/training_10.csv",
    "Source9_6_11": "autopipeline-benchmarks/github-pipelines/length9_6/training_11.csv",
    "Source9_6_12": "autopipeline-benchmarks/github-pipelines/length9_6/training_12.csv",
    "Source9_6_13": "autopipeline-benchmarks/github-pipelines/length9_6/training_13.csv",
    "Source9_6_14": "autopipeline-benchmarks/github-pipelines/length9_6/training_14.csv",
    "Source9_6_15": "autopipeline-benchmarks/github-pipelines/length9_6/training_15.csv",
    "Source9_6_16": "autopipeline-benchmarks/github-pipelines/length9_6/training_16.csv",
}

source_names = [
    "Source9_6_0", "Source9_6_1", "Source9_6_2", "Source9_6_3", "Source9_6_4",
    "Source9_6_5", "Source9_6_6", "Source9_6_7", "Source9_6_8", "Source9_6_9",
    "Source9_6_10", "Source9_6_11", "Source9_6_12", "Source9_6_13", "Source9_6_14",
    "Source9_6_15", "Source9_6_16"
]

dfs = []
for src in source_names:
    df = pd.read_csv(paths[src], index_col=0)
    df = df[['country', 'cpi']]
    df['country'] = df['country'].astype(str)
    df['cpi'] = df['cpi'].astype(float)
    dfs.append(df)

all_data = pd.concat(dfs, ignore_index=True)

# Group by 'country' and aggregate mean of 'cpi'
result = all_data.groupby('country', as_index=False).agg({'cpi': 'mean'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_6/target_multisource_mcts.csv", index=False)