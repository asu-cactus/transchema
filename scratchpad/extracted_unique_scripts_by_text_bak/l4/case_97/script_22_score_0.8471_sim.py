import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

df0['Fare_x'] = 25.100682
df0['Fare_y'] = 274

df0 = df0.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'Age': 'float64',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Fare': 'float64',
    'Cabin': 'string',
    'Embarked': 'string',
    'Fare_x': 'float64',
    'Fare_y': 'int64'
})

df0.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)