import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

fare_x_value = df0['Fare'].mean()
fare_y_value = len(df0)

df0 = df0.copy()

df0['Fare_x'] = fare_x_value
df0['Fare_y'] = fare_y_value

df0['Fare_y'] = df0['Fare_y'].astype('Int64')

df0 = df0[['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']]

df_filtered = df0.dropna(subset=['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Embarked', 'Fare_x', 'Fare_y'])

df_filtered.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv")