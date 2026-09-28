import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_49/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_49/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_49/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_49/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length3_49/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

result = pd.DataFrame()
result['title'] = df['title'].astype(str)
result['min_rank'] = pd.to_numeric(df['rank_on_list'], errors='coerce').fillna(0).astype(int)
result['max_weeks_on_list'] = pd.to_numeric(df['weeks_on_list'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_49/target_multisource_mcts.csv", index=False)