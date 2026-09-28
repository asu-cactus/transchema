import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)
df0_filtered = df0[df0['Embarked'].notnull()]

df_joined = pd.merge(df0_filtered, df0_filtered, on='PassengerId', suffixes=('_x', '_y'))

df_joined['PassengerId'] = df_joined['PassengerId'].astype(int)
df_joined['Survived'] = df_joined['Survived_x'].astype(int)
df_joined['Pclass'] = df_joined['Pclass_x'].astype(int)
df_joined['Name'] = df_joined['Name_x'].astype(str)
df_joined['Sex'] = df_joined['Sex_x'].astype(str)
df_joined['Age'] = pd.to_numeric(df_joined['Age_x'], errors='coerce')
df_joined['SibSp'] = df_joined['SibSp_x'].astype(int)
df_joined['Parch'] = df_joined['Parch_x'].astype(int)
df_joined['Ticket'] = df_joined['Ticket_x'].astype(str)
df_joined['Fare'] = pd.to_numeric(df_joined['Fare_x'], errors='coerce')
df_joined['Cabin'] = df_joined['Cabin_x'].astype(str).replace('nan', pd.NA)
df_joined['Embarked'] = df_joined['Embarked_x'].astype(str)
df_joined['Fare_x'] = pd.to_numeric(df_joined['Fare_x'], errors='coerce')
df_joined['Fare_y'] = df_joined['Fare_y'].fillna(0).astype(int)

result = df_joined[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)