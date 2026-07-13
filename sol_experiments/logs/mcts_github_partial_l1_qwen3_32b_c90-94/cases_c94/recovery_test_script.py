import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_94/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_94/test_1.csv', index_col=0)

source0 = source0.astype({'Date': 'str', 'IsHoliday': 'str'})
source1 = source1.astype({'ID': 'float', 'shop_id': 'float', 'item_id': 'float'})

for col in ['Store', 'Dept', 'Weekly_Sales']:
    source0[col] = pd.to_numeric(source0[col], errors='coerce')

result = pd.concat([source0, source1], axis=0, ignore_index=True)
result = result[['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']]

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts_recovery_test_val.csv', index=False)