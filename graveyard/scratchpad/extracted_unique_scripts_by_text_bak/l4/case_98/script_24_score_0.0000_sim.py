import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv"
source0_copy_path = "autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df0_copy = pd.read_csv(source0_copy_path, index_col=0)

df_merged = pd.merge(df0, df0_copy, on="PassengerId", suffixes=('_x', '_y'))

target_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

df_result = df_merged[target_columns]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv")