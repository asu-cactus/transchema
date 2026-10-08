import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_2.csv", index_col=0)

df = source0.merge(source1, on="PassengerId", suffixes=("", "_x"))
df = df.merge(source2, on="PassengerId", suffixes=("", "_y"))

target = df[[
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch", "Ticket", "Fare", "Cabin", "Embarked",
    "Fare_x", "Fare_y"
]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)