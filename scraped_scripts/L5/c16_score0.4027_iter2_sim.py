import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_16/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_16/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_16/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_16/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_16/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

age_group_map = {
    "Age 18 to 24": 1,
    "Age 25 to 34": 2,
    "Age 35 to 44": 3,
    "Age 45 to 54": 4,
    "Age 55 to 64": 5,
    "Age 65 to 74": 6,
    "Age 75 or older": 7,
    "Refused": 8
}

sex_map = {
    "Female": 1,
    "Male": 2,
    "Refused": 3
}

df['Age Group'] = df['Age Group'].map(age_group_map)
df['Sex'] = df['Sex'].map(sex_map)

df = df.reset_index(drop=True)
df.index.name = 'index'
df = df.reset_index()

cols = ['index', 'Age Group', 'Sex', "Don't know/Refused/Missing", 'Normal Weight', 'Obese', 'Overweight', 'Underweight']
df = df[cols]

df = df.astype({
    'index': 'int64',
    'Age Group': 'Int64',
    'Sex': 'Int64',
    "Don't know/Refused/Missing": 'Int64',
    'Normal Weight': 'Int64',
    'Obese': 'Int64',
    'Overweight': 'Int64',
    'Underweight': 'Int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_16/target_multisource_mcts.csv", index=False)