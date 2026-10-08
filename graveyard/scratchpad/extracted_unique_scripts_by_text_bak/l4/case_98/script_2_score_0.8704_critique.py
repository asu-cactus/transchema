import pandas as pd

# Read both source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_1.csv", index_col=0)

# Rename Fare columns to Fare_x and Fare_y to distinguish after join
df0_renamed = df0.rename(columns={'Fare': 'Fare_x'})
df1_renamed = df1.rename(columns={'Fare': 'Fare_y'})

# Join on PassengerId (primary key)
df = pd.merge(df0_renamed, df1_renamed[['PassengerId', 'Fare_y']], on='PassengerId', how='inner')

# The target schema columns:
target_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 
               'Ticket', 'Fare_x', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# Note: 'Fare_x' appears twice in the above list by mistake, fix it:
target_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 
               'Ticket', 'Fare_x', 'Cabin', 'Embarked', 'Fare_y']

# Select columns in target order
df = df[target_cols]

# Cast types according to target schema
df['PassengerId'] = df['PassengerId'].astype(int)
df['Survived'] = df['Survived'].astype(int)
df['Pclass'] = df['Pclass'].astype(int)
df['Name'] = df['Name'].astype(str)
df['Sex'] = df['Sex'].astype(str)
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
df['SibSp'] = df['SibSp'].astype(int)
df['Parch'] = df['Parch'].astype(int)
df['Ticket'] = df['Ticket'].astype(str)
df['Fare_x'] = pd.to_numeric(df['Fare_x'], errors='coerce')
df['Cabin'] = df['Cabin'].astype(str).replace('nan', pd.NA)
df['Embarked'] = df['Embarked'].astype(str).replace('nan', pd.NA)
df['Fare_y'] = pd.to_numeric(df['Fare_y'], errors='coerce')

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)