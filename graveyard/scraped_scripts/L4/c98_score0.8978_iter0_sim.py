import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

result = df0.groupby("PassengerId", as_index=False).first()

result["Fare_x"] = result["Fare"]
result["Fare_y"] = result["Fare"]

result = result[["PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch", "Ticket", "Fare", "Cabin", "Embarked", "Fare_x", "Fare_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)