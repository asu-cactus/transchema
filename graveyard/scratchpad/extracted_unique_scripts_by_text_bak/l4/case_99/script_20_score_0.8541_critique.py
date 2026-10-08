import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv"
source0_copy_path = "autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df0_copy = pd.read_csv(source0_copy_path, index_col=0)

# Perform inner join on PassengerId
merged = pd.merge(df0, df0_copy[['PassengerId', 'Fare']], on='PassengerId', how='inner', suffixes=('', '_y'))

# Rename columns to match target schema
merged.rename(columns={'Fare': 'Fare_x', 'Fare_y': 'Fare_y'}, inplace=True)

# Reorder columns to match target schema exactly
target_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
                  'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# The original 'Fare' column is kept as 'Fare' (from df0), 'Fare_x' is from df0 (renamed), 'Fare_y' is from df0_copy
# But the target schema has 'Fare' (float) and also 'Fare_x' and 'Fare_y' (float).
# The source df0 has 'Fare' column, so keep it as is.
# We already have 'Fare_x' and 'Fare_y' from the merge, but 'Fare_x' is the original 'Fare' renamed.
# To avoid confusion, keep original 'Fare' as is, and add 'Fare_x' and 'Fare_y' as the two 'Fare' columns from both tables.

# So we need to keep original 'Fare' from df0 (not renamed), and add 'Fare_x' and 'Fare_y' from the join.
# But we renamed 'Fare' to 'Fare_x' above, so revert that.

# Let's fix this: do not rename 'Fare' in df0, only keep 'Fare_x' and 'Fare_y' from the join.

# So redo merge with suffixes=('_x', '_y') and keep original 'Fare' from df0.

merged = pd.merge(df0, df0_copy[['PassengerId', 'Fare']], on='PassengerId', how='inner', suffixes=('_x', '_y'))

# Now merged has columns: all from df0 + 'Fare_y' from df0_copy
# The original 'Fare' from df0 is 'Fare_x' now, but target schema expects 'Fare' (original), plus 'Fare_x' and 'Fare_y'.

# So rename 'Fare_x' back to 'Fare' to match target schema
merged.rename(columns={'Fare_x': 'Fare'}, inplace=True)

# Now add 'Fare_x' and 'Fare_y' columns:
# 'Fare_x' = 'Fare' from df0 (which is now 'Fare')
# 'Fare_y' = 'Fare_y' from df0_copy

# But target schema has both 'Fare_x' and 'Fare_y' columns in addition to 'Fare' column.
# The target examples show 'Fare' column as original fare, and 'Fare_x' and 'Fare_y' as additional fare columns.

# Since we only have two source tables (same), the target schema likely expects:
# - 'Fare' from df0 (original)
# - 'Fare_x' from df0 (same as 'Fare')
# - 'Fare_y' from df0_copy

# So create 'Fare_x' as a copy of 'Fare' column.

merged['Fare_x'] = merged['Fare']
# 'Fare_y' is already present.

# Now drop any duplicated columns from df0_copy except 'Fare_y' and 'PassengerId' (used for join)
# The merge already dropped duplicated columns except 'Fare_y'.

# Reorder columns to match target schema exactly
final_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
                 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

merged = merged[final_columns]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)