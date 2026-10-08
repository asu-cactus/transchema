import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Compute Fare_x: mean Fare per Embarked (float)
fare_x = df0.groupby('Embarked')['Fare'].mean().rename('Fare_x')

# Compute Fare_y: count of PassengerId per Pclass (integer)
fare_y = df0.groupby('Pclass')['PassengerId'].count().rename('Fare_y')

# Merge aggregates back to main dataframe
df = df0.merge(fare_x, on='Embarked', how='left').merge(fare_y, on='Pclass', how='left')

# Ensure Fare_y is integer type
df['Fare_y'] = df['Fare_y'].astype('Int64')

# Group by PassengerId (unique key), aggregate other columns by first to remove duplicates and match target row count
agg_dict = {
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
}

df = df.groupby('PassengerId', as_index=False).agg(agg_dict)

# Reorder columns to match target schema
target_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df = df[target_cols]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)