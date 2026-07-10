import pandas as pd

df_left = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df_right = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

df_right = df_right.rename(columns={'Fare': 'Fare_y'})

df_merged = pd.merge(df_left, df_right[['PassengerId', 'Fare_y']], on='PassengerId', how='inner')

df_merged['Fare_x'] = df_merged['Fare']  # left Fare as Fare_x

cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df_final = df_merged[cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)