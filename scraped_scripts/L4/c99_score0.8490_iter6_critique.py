import pandas as pd
import numpy as np

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

# Filter out rows with missing PassengerId (if any)
df_filtered = df0[df0["PassengerId"].notnull()]

# Add Fare_x and Fare_y columns as NaN to match target schema
df_filtered["Fare_x"] = np.nan
df_filtered["Fare_y"] = np.nan

# Ensure columns order and types as target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
result = df_filtered[final_cols]

# Cast types according to target schema
result["PassengerId"] = result["PassengerId"].astype(int)
result["Survived"] = result["Survived"].astype(int)
result["Pclass"] = result["Pclass"].astype(int)
result["Name"] = result["Name"].astype(str)
result["Sex"] = result["Sex"].astype(str)
result["Age"] = result["Age"].astype(float)
result["SibSp"] = result["SibSp"].astype(int)
result["Parch"] = result["Parch"].astype(int)
result["Ticket"] = result["Ticket"].astype(str)
result["Fare"] = result["Fare"].astype(float)
# Cabin and Embarked may have NaNs, convert to string but keep NaNs as is
result["Cabin"] = result["Cabin"].astype(object)
result["Embarked"] = result["Embarked"].astype(object)
result["Fare_x"] = result["Fare_x"].astype(float)
result["Fare_y"] = result["Fare_y"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)