import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_49/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Sex'] = df['Sex'].astype(str)
sex_map = {k: v for v, k in enumerate(sorted(df['Sex'].unique()))}
df['Sex'] = df['Sex'].map(sex_map)

group_cols = ['Age Group', 'Sex']
agg_cols = ["Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']

result = df.groupby(group_cols, as_index=False)[agg_cols].sum()

result = result.astype({
    "Don't know/Refused/Missing": 'int64',
    'Normal Weight': 'int64',
    'Obese': 'int64',
    'Overweight': 'int64',
    'Underweight': 'int64',
    'Sex': 'int64',
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_49/target_multisource_mcts.csv", index=False)