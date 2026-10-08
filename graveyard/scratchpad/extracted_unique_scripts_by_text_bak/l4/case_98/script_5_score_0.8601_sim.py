import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

df = pd.concat([df0], ignore_index=True)

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
df['Cabin'] = df['Cabin'].astype(str).replace('nan', pd.NA)
df['Embarked'] = df['Embarked'].astype(str).replace('nan', pd.NA)

df['Fare_x'] = df['Fare']
df['Fare_y'] = df['Fare']

df = df[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)