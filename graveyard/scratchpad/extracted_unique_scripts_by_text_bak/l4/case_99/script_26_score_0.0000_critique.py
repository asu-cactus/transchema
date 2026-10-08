import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# Join the table with itself on PassengerId to get Fare_x and Fare_y
df_joined = pd.merge(df0, df0, on="PassengerId", suffixes=('_x', '_y'))

# Group by PassengerId (unique key) and aggregate by taking first for all columns
df_grouped = df_joined.groupby('PassengerId', as_index=False).agg({
    'Survived_x': 'first',
    'Pclass_x': 'first',
    'Name_x': 'first',
    'Sex_x': 'first',
    'Age_x': 'first',
    'SibSp_x': 'first',
    'Parch_x': 'first',
    'Ticket_x': 'first',
    'Fare_x': 'first',
    'Cabin_x': 'first',
    'Embarked_x': 'first',
    'Fare_x': 'first',  # repeated but harmless, will be overwritten
    'Fare_y': 'first'
})

# Rename columns to match target schema
df_grouped.rename(columns={
    'Survived_x': 'Survived',
    'Pclass_x': 'Pclass',
    'Name_x': 'Name',
    'Sex_x': 'Sex',
    'Age_x': 'Age',
    'SibSp_x': 'SibSp',
    'Parch_x': 'Parch',
    'Ticket_x': 'Ticket',
    'Fare_x': 'Fare',
    'Cabin_x': 'Cabin',
    'Embarked_x': 'Embarked'
}, inplace=True)

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

# Convert types to match target schema
df_grouped['PassengerId'] = df_grouped['PassengerId'].astype('Int64')
df_grouped['Survived'] = df_grouped['Survived'].astype('Int64')
df_grouped['Pclass'] = df_grouped['Pclass'].astype('Int64')
df_grouped['SibSp'] = df_grouped['SibSp'].astype('Int64')
df_grouped['Parch'] = df_grouped['Parch'].astype('Int64')
df_grouped['Age'] = pd.to_numeric(df_grouped['Age'], errors='coerce')
df_grouped['Fare'] = pd.to_numeric(df_grouped['Fare'], errors='coerce')
df_grouped['Fare_x'] = pd.to_numeric(df_grouped['Fare_x'], errors='coerce')
df_grouped['Fare_y'] = pd.to_numeric(df_grouped['Fare_y'], errors='coerce')

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)