import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_97/training_0.csv", index_col=0)

agg_df = df0.groupby("PassengerId").agg({
    "Survived": "max",
    "Pclass": "min",
    "Age": "mean",
    "SibSp": "sum",
    "Parch": "sum",
    "Fare": "mean"
}).reset_index()

agg_df.rename(columns={
    "Survived": "Survived",
    "Pclass": "Pclass",
    "Age": "Age",
    "SibSp": "SibSp",
    "Parch": "Parch",
    "Fare": "Fare"
}, inplace=True)

# Merge back the non-aggregated columns from the original df0 on PassengerId
# Columns to merge: Name, Sex, Ticket, Cabin, Embarked
# Since PassengerId is unique in df0, we can drop duplicates before merge
non_agg_cols = df0[["PassengerId", "Name", "Sex", "Ticket", "Cabin", "Embarked"]].drop_duplicates(subset=["PassengerId"])

merged = pd.merge(agg_df, non_agg_cols, on="PassengerId", how="left")

# Add Fare_x and Fare_y columns as in target schema
# Fare_x: float, Fare_y: integer
# From target examples, Fare_x looks like a float average fare, Fare_y looks like an integer fare count or sum
# We have only one source, so Fare_y can be the count of fares per PassengerId (or sum of Fare rounded)
# Let's create Fare_x as the aggregated mean Fare (already in merged['Fare'])
merged["Fare_x"] = merged["Fare"]
# Fare_y as sum of Fare rounded to int
fare_sum = df0.groupby("PassengerId")["Fare"].sum().reset_index()
fare_sum.rename(columns={"Fare": "Fare_y"}, inplace=True)
fare_sum["Fare_y"] = fare_sum["Fare_y"].round().astype("Int64")
merged = pd.merge(merged, fare_sum, on="PassengerId", how="left")

# Reorder columns to match target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
# Ensure types match target schema
merged = merged[final_cols]

merged["PassengerId"] = merged["PassengerId"].astype(int)
merged["Survived"] = merged["Survived"].astype(int)
merged["Pclass"] = merged["Pclass"].astype(int)
merged["Name"] = merged["Name"].astype(str)
merged["Sex"] = merged["Sex"].astype(str)
merged["Age"] = merged["Age"].astype(float)
merged["SibSp"] = merged["SibSp"].astype(int)
merged["Parch"] = merged["Parch"].astype(int)
merged["Ticket"] = merged["Ticket"].astype(str)
merged["Fare"] = merged["Fare"].astype(float)
merged["Cabin"] = merged["Cabin"].astype(str)
merged["Embarked"] = merged["Embarked"].astype(str)
merged["Fare_x"] = merged["Fare_x"].astype(float)
merged["Fare_y"] = merged["Fare_y"].astype("Int64")

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_97/target_multisource_mcts.csv", index=False)