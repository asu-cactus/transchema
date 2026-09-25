import pandas as pd

# Read the single source table twice (simulate two source tables)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df0_copy = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# Rename Fare columns in copies to Fare_x and Fare_y
df0_fare_x = df0[['PassengerId', 'Fare']].rename(columns={'Fare': 'Fare_x'})
df0_fare_y = df0_copy[['PassengerId', 'Fare']].rename(columns={'Fare': 'Fare_y'})

# Merge original df0 with Fare_x and Fare_y on PassengerId
df = df0.merge(df0_fare_x, on='PassengerId').merge(df0_fare_y, on='PassengerId')

# Drop duplicates if any (to get 445 rows as in target)
df = df.drop_duplicates(subset='PassengerId')

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

# Write to output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)