import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Drop rows with NaN in PassengerId (primary key)
df0 = df0.dropna(subset=['PassengerId'])

# Cast columns to correct types
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
    'Embarked': 'string'
})

# Create Fare_x and Fare_y columns without assignment by using assign()
df0 = df0.assign(
    Fare_x = df0['Fare'].astype(float),
    Fare_y = df0['Fare'].astype(int)
)

# Reorder columns to match target schema exactly
df0 = df0[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)