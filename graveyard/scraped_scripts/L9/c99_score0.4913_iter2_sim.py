import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_99/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_9.csv",
]

grouped_dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    grouped = df.groupby(['admit', 'prestige'], as_index=False).agg(
        admit_count=('admit', 'count'),
        gre_avg=('gre', 'mean'),
        gpa_avg=('gpa', 'mean')
    )
    grouped_dfs.append(grouped)

combined = pd.concat(grouped_dfs, ignore_index=True)

final = combined.groupby(['admit', 'prestige'], as_index=False).agg(
    admit=('admit_count', 'sum'),
    gre=('gre_avg', 'mean'),
    gpa=('gpa_avg', 'mean')
)

final = final.rename(columns={'admit': 'admit', 'gre': 'gre', 'gpa': 'gpa', 'prestige': 'prestige'})

final['admit'] = final['admit'].astype(int)
final['gre'] = final['gre'].round().astype(int)
final['gpa'] = final['gpa'].astype(float)
final['prestige'] = final['prestige'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_99/target_multisource_mcts.csv", index=False)