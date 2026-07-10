import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv"
df0 = pd.read_csv(src0_path, index_col=0)

df_joined = pd.merge(df0, df0, on="PassengerId", suffixes=('_x', '_y'))

cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
result = df_joined[cols + ['Fare_x', 'Fare_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)