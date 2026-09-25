import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Filter out rows with missing Embarked
df_filtered = df0[df0['Embarked'].notnull()]

# Aggregate: group by Embarked, compute mean Fare as Fare_x and count PassengerId as Fare_y
agg = df_filtered.groupby('Embarked').agg(
    Fare_x=('Fare', 'mean'),
    Fare_y=('PassengerId', 'count')
).reset_index()

# Join original filtered data with aggregated data on Embarked
df_merged = pd.merge(df_filtered, agg, on='Embarked', how='left')

# Ensure Fare_y is integer as in target schema
df_merged['Fare_y'] = df_merged['Fare_y'].astype(int)

# Select columns as per target schema
result = df_merged[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
                    'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)