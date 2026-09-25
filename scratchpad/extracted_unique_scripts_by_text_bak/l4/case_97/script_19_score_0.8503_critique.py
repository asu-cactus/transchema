import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Join on PassengerId
df = pd.merge(df0, df1, on='PassengerId', suffixes=('', '_dup'))

# Construct Fare_x as float from original Fare (left table)
# Construct Fare_y as int from original Fare (right table, with suffix '_dup')
df['Fare_x'] = df['Fare'].astype(float)
df['Fare_y'] = df['Fare_dup'].astype(int)

# Select columns as per target schema
df = df[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)