import pandas as pd

# Read the source table twice to simulate two source tables with same schema
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)
df0_copy = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# Rename columns in the copy to avoid collision except PassengerId (join key)
df0_copy = df0_copy.add_suffix('_copy')
df0_copy = df0_copy.rename(columns={'PassengerId_copy': 'PassengerId'})

# Join on PassengerId
result = pd.merge(df0, df0_copy, on='PassengerId', how='inner')

# Select and rename columns to match target schema
result = result[[
    'PassengerId',
    'Survived',
    'Pclass',
    'Name',
    'Sex',
    'Age',
    'SibSp',
    'Parch',
    'Ticket',
    'Fare',
    'Cabin',
    'Embarked',
    'Fare_copy',  # This corresponds to Fare_y in target
]]

# Rename Fare columns to match target schema
result = result.rename(columns={
    'Fare': 'Fare_x',
    'Fare_copy': 'Fare_y'
})

# Reorder columns to exactly match target schema
result = result[[
    'PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
    'Ticket', 'Fare_x', 'Cabin', 'Embarked', 'Fare_y'
]]

# The target schema has Fare (float) before Cabin, but the target examples show Fare, Cabin, Embarked, Fare_x, Fare_y
# The target schema in the prompt is:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
# So we need to add 'Fare' column as well. The source has only one Fare column per table.
# We can keep 'Fare' from the first table as 'Fare' column.

# Add 'Fare' column from first table (same as Fare_x)
result['Fare'] = result['Fare_x']

# Reorder columns again to match target schema exactly
result = result[[
    'PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
    'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y'
]]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)