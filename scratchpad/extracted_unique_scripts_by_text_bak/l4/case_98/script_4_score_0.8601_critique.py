import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# Create Fare_x and Fare_y as duplicates of Fare
df0['Fare_x'] = df0['Fare']
df0['Fare_y'] = df0['Fare']

# Select columns in target schema order
cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
        'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

df0 = df0[cols]

# Group by PassengerId to remove duplicates, take first of each column
df_result = df0.groupby('PassengerId', as_index=False).agg({
    'Survived': 'first',
    'Pclass': 'first',
    'Name': 'first',
    'Sex': 'first',
    'Age': 'first',
    'SibSp': 'first',
    'Parch': 'first',
    'Ticket': 'first',
    'Fare': 'first',
    'Cabin': 'first',
    'Embarked': 'first',
    'Fare_x': 'first',
    'Fare_y': 'first'
})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)