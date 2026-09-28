import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

# Add Fare_x as the original Fare (float)
# Add Fare_y as the rounded Fare cast to integer (Int64 to allow NaNs)
df0["Fare_x"] = df0["Fare"]
df0["Fare_y"] = df0["Fare"].round().astype("Int64")

# Reorder columns to match target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 
              'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

df0 = df0[final_cols]

# Ensure types match target schema
df0["PassengerId"] = df0["PassengerId"].astype(int)
df0["Survived"] = df0["Survived"].astype(int)
df0["Pclass"] = df0["Pclass"].astype(int)
df0["Name"] = df0["Name"].astype(str)
df0["Sex"] = df0["Sex"].astype(str)
df0["Age"] = df0["Age"].astype(float)
df0["SibSp"] = df0["SibSp"].astype(int)
df0["Parch"] = df0["Parch"].astype(int)
df0["Ticket"] = df0["Ticket"].astype(str)
df0["Fare"] = df0["Fare"].astype(float)
df0["Cabin"] = df0["Cabin"].astype(str)
df0["Embarked"] = df0["Embarked"].astype(str)
df0["Fare_x"] = df0["Fare_x"].astype(float)
df0["Fare_y"] = df0["Fare_y"].astype("Int64")

# Write output
df0.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)