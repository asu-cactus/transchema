import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_74/test_0.csv', index_col=0)
result = df0.groupby('Gender').agg(
    Purchase_ID=('Purchase ID', 'count'),
    SN=('SN', 'count'),
    Age=('Age', 'count'),
    Item_ID=('Item ID', 'count'),
    Item_Name=('Item Name', 'count'),
    Price=('Price', 'count')
).reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts_recovery_test_val.csv', index=False)