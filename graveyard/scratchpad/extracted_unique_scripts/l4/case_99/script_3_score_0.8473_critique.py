import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# Aggregate mean Fare per Pclass for Fare_x
fare_x_agg = df0.groupby('Pclass', as_index=False)['Fare'].mean().rename(columns={'Fare': 'Fare_x'})

# Aggregate mean Fare per Embarked for Fare_y
fare_y_agg = df0.groupby('Embarked', as_index=False)['Fare'].mean().rename(columns={'Fare': 'Fare_y'})

# Join fare_x_agg on Pclass
df = df0.merge(fare_x_agg, on='Pclass', how='left')

# Join fare_y_agg on Embarked
df = df.merge(fare_y_agg, on='Embarked', how='left')

# Ensure correct dtypes as per target schema
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

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)