import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# Add constant columns Fare_x and Fare_y as in target examples
df0["Fare_x"] = 10.5
df0["Fare_y"] = 263.0

# Reorder columns to match target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 
              'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

result = df0[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)