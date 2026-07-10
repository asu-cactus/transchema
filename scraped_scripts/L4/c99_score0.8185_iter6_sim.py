import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)

agg = df0.groupby("PassengerId").agg({
    "Survived": "max",
    "Pclass": "min",
    "Age": "mean",
    "Ticket": "count"
}).reset_index()

# The target schema has many columns not in source 0, including Name, Sex, SibSp, Parch, Ticket (string), Fare, Cabin, Embarked, Fare_x, Fare_y
# Since only one source table is given, and the partial plan only aggregates some columns, we must fill the missing columns by joining back or filling from source.

# Join aggregated results back to original to get other columns (Name, Sex, SibSp, Parch, Ticket (string), Fare, Cabin, Embarked)
# But since aggregation grouped by PassengerId, and PassengerId is unique in source, we can merge on PassengerId to get other columns.

# However, aggregation changed Survived, Pclass, Age, Ticket count columns, so we keep those from agg, and take other columns from original df0.

# Merge agg with df0 on PassengerId to get other columns
merged = pd.merge(agg, df0.drop(columns=["Survived", "Pclass", "Age", "Ticket"]), on="PassengerId", how="left")

# Rename columns to match target schema
merged.rename(columns={
    "Survived": "Survived",
    "Pclass": "Pclass",
    "Age": "Age",
    "Ticket_x": "Ticket",  # Ticket count is numeric, but target Ticket is string, so keep original Ticket from df0 (Ticket_y)
    "Ticket_y": "Ticket"
}, inplace=True)

# The aggregation count on Ticket is numeric, but target Ticket is string, so keep original Ticket string from df0
# The aggregation count is not needed in final output, so drop it
merged.drop(columns=["Ticket_x"], inplace=True, errors='ignore')

# The target has Fare_x and Fare_y columns, which are not in source0.
# Since only one source is given, we cannot produce Fare_x and Fare_y from multiple sources.
# We will fill Fare_x and Fare_y with NaN to match schema.

merged["Fare_x"] = np.nan
merged["Fare_y"] = np.nan

# Ensure columns order and types as target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
result = merged[final_cols]

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
result["Cabin"] = result["Cabin"].astype(str)
result["Embarked"] = result["Embarked"].astype(str)
result["Fare_x"] = result["Fare_x"].astype(float)
result["Fare_y"] = result["Fare_y"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)