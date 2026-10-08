import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Create Fare_x as float copy of Fare, Fare_y as integer copy of Fare (fill NaN with 0 before int conversion)
df = df0.copy()
df['Fare_x'] = df['Fare'].astype(float)
df['Fare_y'] = df['Fare'].fillna(0).astype(int)

# Ensure types match target schema
df['PassengerId'] = df['PassengerId'].astype(int)
df['Survived'] = df['Survived'].astype(int)
df['Pclass'] = df['Pclass'].astype(int)
df['Name'] = df['Name'].astype(str)
df['Sex'] = df['Sex'].astype(str)
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
df['SibSp'] = df['SibSp'].astype(int)
df['Parch'] = df['Parch'].astype(int)
df['Ticket'] = df['Ticket'].astype(str)
df['Fare'] = pd.to_numeric(df['Fare'], errors='coerce')
df['Cabin'] = df['Cabin'].astype(str)
df['Embarked'] = df['Embarked'].astype(str)
df['Fare_x'] = df['Fare_x'].astype(float)
df['Fare_y'] = df['Fare_y'].astype(int)

# Group by PassengerId (unique key) to ensure uniqueness and correct row count
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

df_final = df.groupby('PassengerId', as_index=False).agg(agg_dict)

# Reorder columns to match target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df_final = df_final[final_cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)