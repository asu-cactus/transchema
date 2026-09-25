import pandas as pd
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)
df0['Age Category'] = df0['Age'].astype(int)
df0['Purchase ID'] = df0['Purchase ID'].astype(int)
df0['SN'] = pd.factorize(df0['SN'])[0] + 1
df0['Purchase Count'] = 1
df0['Gender'] = df0['Gender'].map({'Male':1, 'Female':2}).fillna(0).astype(int)
df0['Item ID'] = df0['Item ID'].astype(int)
df0['Item Name'] = pd.factorize(df0['Item Name'])[0] + 1
df0['Price'] = df0['Price'].astype(float)
grouped = df0.groupby('Age Category').agg({
    'Purchase ID':'count',
    'SN':'count',
    'Purchase Count':'sum',
    'Gender':'max',
    'Item ID':'max',
    'Item Name':'max',
    'Price':['sum','mean']
})
grouped.columns = ['Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Total Purchase Value', 'Average Purchase Price']
grouped = grouped.reset_index()
grouped = grouped.astype({
    'Age Category': int,
    'Purchase ID': int,
    'SN': int,
    'Purchase Count': int,
    'Gender': int,
    'Item ID': int,
    'Item Name': int,
    'Total Purchase Value': float,
    'Average Purchase Price': float
})
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)