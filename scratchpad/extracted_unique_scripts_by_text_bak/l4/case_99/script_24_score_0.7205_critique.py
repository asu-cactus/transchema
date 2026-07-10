import pandas as pd

# Read the same source file twice as two separate tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# Join on PassengerId (primary key)
df = pd.merge(df0, df1, on='PassengerId', suffixes=('_x', '_y'))

# The target schema columns are:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
# After merge, columns from left table have no suffix, right table columns have _y suffix except PassengerId.
# We want to keep the left table columns as is, and add Fare_x and Fare_y from both tables' Fare columns.

# Rename columns to match target schema exactly:
# Left table columns remain the same except Fare column is renamed to Fare (already correct)
# Right table Fare column is Fare_y
# Left table Fare column is Fare_x (from left table's Fare)

# So we rename left Fare to Fare_x, right Fare_y remains Fare_y, and keep left Fare as Fare (target has Fare and Fare_x, Fare_y)
# But target has Fare (float), Fare_x (float), Fare_y (float)
# The source Fare column is duplicated in left and right tables, so:
# - Keep left Fare as Fare
# - Add Fare_x = left Fare
# - Add Fare_y = right Fare

# So we create Fare_x from left Fare, Fare_y from right Fare, and keep Fare as left Fare

df['Fare_x'] = df['Fare']
df['Fare_y'] = df['Fare_y']

# Now keep only the columns in the target schema and in the correct order
target_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df = df[target_columns]

# Cast columns to the exact types as target schema
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