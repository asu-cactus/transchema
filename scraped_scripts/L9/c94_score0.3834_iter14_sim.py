import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_94/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_9.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

for df in dfs:
    df['prestige'] = df['prestige'].astype(int)
    df['admit'] = df['admit'].astype(int)
    df['gre'] = df['gre'].astype(int)
    df['gpa'] = df['gpa'].astype(float)

agg_admit = 0
agg_gre = None
agg_gpa = None
prestige_val = None

for df in dfs:
    if prestige_val is None:
        prestige_val = df['prestige'].iloc[0]
    agg_admit += df['admit'].sum()
    min_gre = df['gre'].min()
    min_gpa = df['gpa'].min()
    if agg_gre is None or min_gre < agg_gre:
        agg_gre = min_gre
    if agg_gpa is None or min_gpa < agg_gpa:
        agg_gpa = min_gpa

result = pd.DataFrame({
    'admit': [agg_admit],
    'gre': [agg_gre],
    'gpa': [agg_gpa],
    'prestige': [prestige_val]
})

result = result.astype({'admit': int, 'gre': int, 'gpa': float, 'prestige': int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_94/target_multisource_mcts.csv", index=False)