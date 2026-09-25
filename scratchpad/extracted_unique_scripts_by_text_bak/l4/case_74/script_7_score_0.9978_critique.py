import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by 'Gender' and count the number of rows per gender
grouped = df0.groupby('Gender').size().reset_index(name='count')

# Prepare the final dataframe with the target schema columns
# Target schema: ['Gender': string, 'Purchase ID': int, 'SN': int, 'Age': int, 'Item ID': int, 'Item Name': int, 'Price': int]
# Assign the count to all integer columns except 'Gender'
result = pd.DataFrame()
result['Gender'] = grouped['Gender']
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    result[col] = grouped['count']

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)