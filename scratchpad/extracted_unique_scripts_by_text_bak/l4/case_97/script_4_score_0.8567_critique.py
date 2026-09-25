import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Compute Fare_x as mean Fare (float)
fare_x = df0["Fare"].mean()

# Compute Fare_y as count of Survived=1 (integer)
fare_y = df0["Survived"].sum()

# Add these as constant columns
df = df0.copy()
df["Fare_x"] = fare_x
df["Fare_y"] = fare_y.astype("Int64")

# Drop rows with any NaN values to match target row count (445)
df = df.dropna()

# Ensure column order matches target schema
target_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df = df[target_columns]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)