import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_49/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_49/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Sex'] = df['Sex'].map({'Female': 10, 'Male': 11, 'Refused': 12}).fillna(df['Sex'])
df['Sex'] = df['Sex'].astype(int)

cols = ['Age Group', 'Sex', "Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']
df = df[cols]

agg_cols = ["Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']

df = df.groupby(['Age Group', 'Sex'], as_index=False)[agg_cols].sum()

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_49/target_multisource_mcts.csv", index=False)