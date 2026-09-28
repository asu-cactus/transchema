import pandas as pd

# Read both source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_1.csv", index_col=0)

# Ensure correct types for df0
df0 = df0.astype({
    'PassengerId': int,
    'Survived': int,
    'Pclass': int,
    'Name': str,
    'Sex': str,
    'Age': float,
    'SibSp': int,
    'Parch': int,
    'Ticket': str,
    'Fare': float,
    'Cabin': str,
    'Embarked': str
})

# Ensure correct types for df1
df1 = df1.astype({
    'PassengerId': int,
    'Survived': int,
    'Pclass': int,
    'Name': str,
    'Sex': str,
    'Age': float,
    'SibSp': int,
    'Parch': int,
    'Ticket': str,
    'Fare': float,
    'Cabin': str,
    'Embarked': str
})

# Join on PassengerId (inner join)
df_merged = pd.merge(df0, df1, on='PassengerId', suffixes=('', '_y'), how='inner')

# Rename columns to match target schema:
# The target schema is:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
# From df_merged:
# - The first Fare column is from df0, rename to Fare_x
# - The second Fare column is from df1, rename to Fare_y
# - The original Fare column from df0 should be renamed to Fare_x
# - The Fare column from df1 is Fare_y (already with suffix '_y')

# Rename Fare columns accordingly
df_merged = df_merged.rename(columns={
    'Fare': 'Fare_x',
    'Fare_y': 'Fare_y'
})

# The target schema has Fare (without suffix) as the Fare from df0 (original Fare column)
# But the target schema shows Fare (float) before Fare_x and Fare_y, so we must keep Fare from df0 as 'Fare'
# So we need to:
# - Keep df0's Fare as 'Fare'
# - Rename df1's Fare to 'Fare_y'
# - Rename df0's Fare to 'Fare_x' is incorrect, because target has Fare and Fare_x and Fare_y
# So the target schema columns are:
# PassengerId, Survived, Pclass, Name, Sex, Age, SibSp, Parch, Ticket, Fare, Cabin, Embarked, Fare_x, Fare_y
# So Fare is from df0 (original Fare)
# Fare_x and Fare_y are additional columns (likely from some other source or calculation)
# But since we only have two sources, and both have Fare, we can assign:
# - Fare: from df0's Fare
# - Fare_x: from df0's Fare (duplicate)
# - Fare_y: from df1's Fare

# So create Fare_x as duplicate of Fare from df0
df_merged['Fare_x'] = df_merged['Fare']
# Fare_y is already from df1's Fare (Fare_y)

# Select and order columns exactly as target schema
final_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df_final = df_merged[final_columns]

# Write to output CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)