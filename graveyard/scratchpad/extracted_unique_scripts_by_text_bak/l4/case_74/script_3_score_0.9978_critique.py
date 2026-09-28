import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by Gender and count the number of purchases per gender
grouped = df0.groupby('Gender', dropna=False).agg({'Purchase ID': 'count'}).reset_index()

# Rename the count column for clarity
grouped = grouped.rename(columns={'Purchase ID': 'count'})

# Prepare the final DataFrame with the target schema
# Gender: string
# Other columns: integer, all set to the count value per gender
result = pd.DataFrame()
result['Gender'] = grouped['Gender'].astype(str)
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    result[col] = grouped['count'].astype('Int64')

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)