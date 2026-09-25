import pandas as pd

# Read the source table twice (simulate two source tables with same schema)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# Rename Fare columns to Fare_x and Fare_y to match target schema
df0_renamed = df0.rename(columns={"Fare": "Fare_x"})
df1_renamed = df1.rename(columns={"Fare": "Fare_y"})

# Join on PassengerId
df_joined = pd.merge(df0_renamed, df1_renamed, on="PassengerId", suffixes=('_left', '_right'))

# Select columns as per target schema
# Columns from df0_renamed (left) except Fare (replaced by Fare_x)
# Columns from df1_renamed (right) only Fare_y
# Avoid duplicate columns from right side except Fare_y

# Columns to keep from left (df0_renamed)
left_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare_x', 'Cabin', 'Embarked']

# Fare_y from right
right_cols = ['Fare_y']

# Extract columns
df_result = df_joined[left_cols + right_cols]

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)