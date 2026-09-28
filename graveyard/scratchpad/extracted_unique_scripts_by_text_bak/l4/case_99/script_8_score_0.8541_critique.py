import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

df0['Fare_x'] = 25.100682
df0['Fare_y'] = 10.5

# Group by PassengerId (primary key) to ensure uniqueness and aggregate other columns
agg_dict = {
    'Survived': 'first',
    'Pclass': 'first',
    'Name': 'first',
    'Sex': 'first',
    'Age': 'mean',
    'SibSp': 'first',
    'Parch': 'first',
    'Ticket': 'first',
    'Fare': 'mean',
    'Cabin': 'first',
    'Embarked': 'first',
    'Fare_x': 'first',
    'Fare_y': 'first'
}

df = df0.groupby('PassengerId', as_index=False).agg(agg_dict)

# Cast columns to target types
df = df.astype({
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
    'Fare_y': 'float64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)