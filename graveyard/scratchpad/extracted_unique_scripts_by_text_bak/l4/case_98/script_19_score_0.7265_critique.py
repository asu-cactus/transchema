import pandas as pd

# Read the same source twice
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# Join on PassengerId
df_joined = pd.merge(df0, df1, on='PassengerId', suffixes=('', '_y'))

# Rename Fare columns to match target schema
df_joined = df_joined.rename(columns={'Fare': 'Fare_x', 'Fare_y': 'Fare_y'})

# The target schema expects Fare (original), Fare_x, Fare_y
# The original Fare column is from df0, which is now Fare_x, so we need to restore 'Fare' column from Fare_x
# But target schema has Fare, Fare_x, Fare_y, so we keep Fare from df0 (which is Fare_x now), and also keep Fare_x and Fare_y
# Actually, the target schema columns are:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
# So we need to keep 'Fare' from df0 as 'Fare', and also have 'Fare_x' and 'Fare_y' from the join.
# But after merge, 'Fare' from df0 is 'Fare', and 'Fare' from df1 is 'Fare_y'.
# So we can do:
df_joined['Fare_x'] = df_joined['Fare']
df_joined['Fare'] = df_joined['Fare']  # keep original Fare as is
# 'Fare_y' is already present from df1

# Select and reorder columns to match target schema exactly
final_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df_final = df_joined[final_columns]

# Cast columns to correct types
df_final = df_final.astype({
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

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)