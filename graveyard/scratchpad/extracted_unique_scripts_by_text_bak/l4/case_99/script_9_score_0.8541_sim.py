import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

df0['PassengerId'] = df0['PassengerId'].astype(int)
df0['Survived'] = df0['Survived'].astype(int)
df0['Pclass'] = df0['Pclass'].astype(int)
df0['Name'] = df0['Name'].astype(str)
df0['Sex'] = df0['Sex'].astype(str)
df0['Age'] = df0['Age'].astype(float)
df0['SibSp'] = df0['SibSp'].astype(int)
df0['Parch'] = df0['Parch'].astype(int)
df0['Ticket'] = df0['Ticket'].astype(str)
df0['Fare'] = df0['Fare'].astype(float)
df0['Cabin'] = df0['Cabin'].astype(str)
df0['Embarked'] = df0['Embarked'].astype(str)

df0['Fare_x'] = df0['Fare']
df0['Fare_y'] = df0['Fare']

df0.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)