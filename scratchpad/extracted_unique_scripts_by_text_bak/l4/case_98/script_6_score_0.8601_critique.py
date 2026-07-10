import pandas as pd

# Read the single source table twice (simulate two sources)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# Ensure correct types for df0
df0 = df0.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Cabin': 'string',
    'Embarked': 'string'
})
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce')
df0['Fare'] = pd.to_numeric(df0['Fare'], errors='coerce')
df0['Cabin'] = df0['Cabin'].replace('nan', pd.NA)
df0['Embarked'] = df0['Embarked'].replace('nan', pd.NA)

# Ensure correct types for df1 (same as df0)
df1 = df1.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Cabin': 'string',
    'Embarked': 'string'
})
df1['Age'] = pd.to_numeric(df1['Age'], errors='coerce')
df1['Fare'] = pd.to_numeric(df1['Fare'], errors='coerce')
df1['Cabin'] = df1['Cabin'].replace('nan', pd.NA)
df1['Embarked'] = df1['Embarked'].replace('nan', pd.NA)

# Rename columns in df1 to avoid collision except the join key
df1_renamed = df1.rename(columns={
    'Survived': 'Survived_y',
    'Pclass': 'Pclass_y',
    'Name': 'Name_y',
    'Sex': 'Sex_y',
    'Age': 'Age_y',
    'SibSp': 'SibSp_y',
    'Parch': 'Parch_y',
    'Ticket': 'Ticket_y',
    'Fare': 'Fare_y',
    'Cabin': 'Cabin_y',
    'Embarked': 'Embarked_y'
})

# Join on PassengerId
df_joined = pd.merge(df0, df1_renamed, on='PassengerId', how='inner', suffixes=('', '_y'))

# Now construct the final dataframe with columns as in target schema:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# According to the target, Fare_x and Fare_y are the two Fare columns from the two sources.
# We can take Fare_x = df0['Fare'], Fare_y = df1['Fare']

df_final = pd.DataFrame({
    'PassengerId': df_joined['PassengerId'],
    'Survived': df_joined['Survived'],
    'Pclass': df_joined['Pclass'],
    'Name': df_joined['Name'],
    'Sex': df_joined['Sex'],
    'Age': df_joined['Age'],
    'SibSp': df_joined['SibSp'],
    'Parch': df_joined['Parch'],
    'Ticket': df_joined['Ticket'],
    'Fare': df_joined['Fare'],
    'Cabin': df_joined['Cabin'],
    'Embarked': df_joined['Embarked'],
    'Fare_x': df_joined['Fare'],
    'Fare_y': df_joined['Fare_y']
})

# Group by PassengerId to remove duplicates if any (no aggregation needed as PassengerId is unique)
df_final = df_final.groupby('PassengerId', as_index=False).first()

# Ensure correct dtypes matching target schema
df_final = df_final.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Cabin': 'string',
    'Embarked': 'string',
    'Fare_x': 'float64',
    'Fare_y': 'float64'
})
df_final['Age'] = pd.to_numeric(df_final['Age'], errors='coerce')
df_final['Fare'] = pd.to_numeric(df_final['Fare'], errors='coerce')

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)