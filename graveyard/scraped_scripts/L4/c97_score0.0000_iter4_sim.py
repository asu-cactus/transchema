import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

df = df0.merge(df0, on="PassengerId", suffixes=('_x', '_y'))

df = df.rename(columns={
    'Survived': 'Survived',
    'Pclass': 'Pclass',
    'Name': 'Name',
    'Sex': 'Sex',
    'Age': 'Age',
    'SibSp': 'SibSp',
    'Parch': 'Parch',
    'Ticket': 'Ticket',
    'Fare_x': 'Fare_x',
    'Fare_y': 'Fare_y',
    'Cabin': 'Cabin',
    'Embarked': 'Embarked',
    'Fare': 'Fare'
})

df = df[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df['Fare_y'] = df['Fare_y'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv")