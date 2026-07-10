import pandas as pd

# Read both source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_1.csv", index_col=0)

# Join on PassengerId
df = pd.merge(df0, df1, on='PassengerId', how='inner', suffixes=('_x', '_y'))

# Select and reorder columns to match target schema
df = df[['PassengerId', 
         'Survived_x', 'Pclass_x', 'Name_x', 'Sex_x', 'Age_x', 'SibSp_x', 'Parch_x', 'Ticket_x', 'Fare_x', 'Cabin_x', 'Embarked_x',
         'Fare_y']]

# Rename columns to target schema names
df.columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_y']

# Cast columns to correct types
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
    'Fare_y': 'float64'
})

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)