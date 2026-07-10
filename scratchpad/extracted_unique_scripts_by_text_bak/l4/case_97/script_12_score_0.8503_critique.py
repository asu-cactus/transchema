import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Add Fare_x and Fare_y columns as float and int versions of Fare
df0['Fare_x'] = df0['Fare'].astype(float)
df0['Fare_y'] = df0['Fare'].astype(int)

# Cast columns to match target schema types exactly
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

# The target has 445 rows, source has 446 rows, so drop rows with missing PassengerId or duplicates if any
# Since PassengerId is unique, drop rows with NaN PassengerId or duplicates
df0 = df0.dropna(subset=['PassengerId'])
df0 = df0.drop_duplicates(subset=['PassengerId'])

# Write output with exact column order as target schema
target_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df0[target_columns].to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)