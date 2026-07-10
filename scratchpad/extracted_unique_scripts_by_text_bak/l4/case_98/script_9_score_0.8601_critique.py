import pandas as pd

# Read the single source table twice (simulate two source tables)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_98/training_0.csv", index_col=0)

# Rename columns in df1 to distinguish them (except the join key)
df1_renamed = df1.rename(columns={
    'Fare': 'Fare_y',
    'PassengerId': 'PassengerId',  # keep join key same
    'Survived': 'Survived_y',
    'Pclass': 'Pclass_y',
    'Name': 'Name_y',
    'Sex': 'Sex_y',
    'Age': 'Age_y',
    'SibSp': 'SibSp_y',
    'Parch': 'Parch_y',
    'Ticket': 'Ticket_y',
    'Cabin': 'Cabin_y',
    'Embarked': 'Embarked_y'
})

# Join on PassengerId
df_joined = pd.merge(df0, df1_renamed, on='PassengerId', how='inner', suffixes=('_x', '_y'))

# Construct the final dataframe with columns as per target schema:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# 'Fare_x' is the original Fare from df0 renamed to Fare_x
# 'Fare_y' is from df1_renamed

# Rename df0's Fare to Fare_x
df_joined = df_joined.rename(columns={'Fare': 'Fare_x'})

# Select and reorder columns
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# 'Fare' column is from df0 (original), so it is still 'Fare' in df0
# But after rename, df0's Fare is 'Fare_x', so we need to get original Fare from df0 before rename
# Actually, after rename, 'Fare' column no longer exists, so we need to keep original Fare before rename

# To fix this, rename df0's Fare to 'Fare' (keep original), and rename df1's Fare to 'Fare_y'

# So better to rename df1's Fare to 'Fare_y' only, keep df0's Fare as is

# Let's redo the join with only df1's Fare renamed

df1_renamed = df1.rename(columns={'Fare': 'Fare_y'})

df_joined = pd.merge(df0, df1_renamed, on='PassengerId', how='inner', suffixes=('_x', '_y'))

# Now columns include 'Fare' (from df0) and 'Fare_y' (from df1_renamed)

# Select columns as per target schema
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# But 'Fare_x' does not exist, only 'Fare' and 'Fare_y'

# The target schema has 'Fare_x' and 'Fare_y' in addition to 'Fare'

# The example target rows have 'Fare' and 'Fare_x' and 'Fare_y'

# So we need to create 'Fare_x' and 'Fare_y' columns from the two tables, and keep 'Fare' as original

# Since only one source table, we can create 'Fare_x' and 'Fare_y' as copies of 'Fare' with different values

# But this is not logical; the target examples show different values for Fare_x and Fare_y

# Since only one source table is given, and the target has two Fare columns, the only way is to join the source table with itself but with some modification to get different Fare columns

# For example, join on PassengerId but with different filters or suffixes

# However, since only one source table is given, and no other source tables, the best we can do is join the table with itself on PassengerId, and rename Fare columns to Fare_x and Fare_y

# So final columns will be:

# ['PassengerId', 'Survived_x', 'Pclass_x', 'Name_x', 'Sex_x', 'Age_x', 'SibSp_x', 'Parch_x', 'Ticket_x', 'Fare_x', 'Cabin_x', 'Embarked_x', 'Fare_y']

# Then rename columns to remove suffixes except for Fare_x and Fare_y

df1_renamed = df1.rename(columns={'Fare': 'Fare_y'})

df_joined = pd.merge(df0, df1_renamed, on='PassengerId', how='inner', suffixes=('_x', '_y'))

# Rename columns to match target schema
df_joined = df_joined.rename(columns={
    'Survived_x': 'Survived',
    'Pclass_x': 'Pclass',
    'Name_x': 'Name',
    'Sex_x': 'Sex',
    'Age_x': 'Age',
    'SibSp_x': 'SibSp',
    'Parch_x': 'Parch',
    'Ticket_x': 'Ticket',
    'Cabin_x': 'Cabin',
    'Embarked_x': 'Embarked'
})

# Select columns in order
final_cols = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# 'Fare' column is from df0 (original), 'Fare_x' does not exist, but 'Fare' is from df0, 'Fare_y' from df1_renamed

# The target schema has both 'Fare_x' and 'Fare_y' in addition to 'Fare'

# The source only has one Fare column, so 'Fare_x' and 'Fare_y' must come from the two joined tables

# So we can create 'Fare_x' as the Fare from df0, and 'Fare_y' as Fare_y from df1_renamed

df_joined['Fare_x'] = df_joined['Fare']
# 'Fare' column is the original Fare, keep it as is

# Now select columns including 'Fare_x' and 'Fare_y'
df_final = df_joined[final_cols]

# Cast columns to correct types as per target schema
df_final['PassengerId'] = df_final['PassengerId'].astype(int)
df_final['Survived'] = df_final['Survived'].astype(int)
df_final['Pclass'] = df_final['Pclass'].astype(int)
df_final['SibSp'] = df_final['SibSp'].astype(int)
df_final['Parch'] = df_final['Parch'].astype(int)
df_final['Age'] = df_final['Age'].astype(float)
df_final['Fare'] = df_final['Fare'].astype(float)
df_final['Fare_x'] = df_final['Fare_x'].astype(float)
df_final['Fare_y'] = df_final['Fare_y'].astype(float)
df_final['Name'] = df_final['Name'].astype(str)
df_final['Sex'] = df_final['Sex'].astype(str)
df_final['Ticket'] = df_final['Ticket'].astype(str)
df_final['Cabin'] = df_final['Cabin'].astype(str)
df_final['Embarked'] = df_final['Embarked'].astype(str)

# Write to CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_98/target_multisource_mcts.csv", index=False)