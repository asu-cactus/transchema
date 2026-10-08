import pandas as pd

# Read all source tables (assuming 3 source tables with same schema)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_99/training_2.csv", index_col=0)

# Rename Fare columns in df1 and df2 to Fare_x and Fare_y to match target schema
df1 = df1.rename(columns={'Fare': 'Fare_x'})
df2 = df2.rename(columns={'Fare': 'Fare_y'})

# Drop columns Fare_x and Fare_y from df0 if exist (to avoid conflicts)
df0 = df0.drop(columns=[col for col in ['Fare_x', 'Fare_y'] if col in df0.columns])

# Join df0 and df1 on PassengerId (inner join)
df01 = pd.merge(df0, df1[['PassengerId', 'Fare_x']], on='PassengerId', how='inner')

# Join the result with df2 on PassengerId (inner join)
df_final = pd.merge(df01, df2[['PassengerId', 'Fare_y']], on='PassengerId', how='inner')

# Ensure the final dataframe columns are exactly as target schema:
# ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']

# The columns from df0 are all except Fare_x and Fare_y, plus Fare
# Add Fare_x and Fare_y from joined tables

# Reorder columns to match target schema
final_columns = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked', 'Fare_x', 'Fare_y']
df_final = df_final[final_columns]

# Set correct dtypes
df_final = df_final.astype({
    'PassengerId': 'int64',
    'Survived': 'int64',
    'Pclass': 'int64',
    'Name': 'string',
    'Sex': 'string',
    'Age': 'float64',
    'SibSp': 'int64',
    'Parch': 'int64',
    'Ticket': 'string',
    'Fare': 'float64',
    'Cabin': 'string',
    'Embarked': 'string',
    'Fare_x': 'float64',
    'Fare_y': 'float64'
})

# Write to output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)