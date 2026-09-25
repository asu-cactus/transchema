import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Group by PassengerId and aggregate by first for all other columns
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
    'Embarked': 'first'
}

df_grouped = df0.groupby('PassengerId', as_index=False).agg(agg_dict)

# Compute Fare_x as mean Fare over all rows
fare_x = df0['Fare'].mean()

# Compute Fare_y as count of rows
fare_y = len(df0)

# Add Fare_x and Fare_y columns
df_grouped['Fare_x'] = fare_x
df_grouped['Fare_y'] = fare_y

# Cast columns to target types
df_grouped = df_grouped.astype({
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

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)