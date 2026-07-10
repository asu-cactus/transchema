import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

join_0 = pd.merge(df0, df1, on="WarID", how="outer", suffixes=('_0', '_1'))
join_1 = pd.merge(join_0, df2, on="WarID", how="outer", suffixes=('', '_2'))
join_2 = pd.merge(join_1, df3, on="WarID", how="outer", suffixes=('', '_3'))

def coalesce_columns(row, col_list):
    for col in col_list:
        if pd.notna(row.get(col)):
            return row[col]
    return None

result = pd.DataFrame()
result['IsInternational'] = join_2['IsInternational'].fillna(0).astype(int)
result['WarID'] = join_2['WarID'].astype(int)
result['WarShortName'] = join_2.apply(lambda r: coalesce_columns(r, ['WarShortName_0', 'WarShortName', 'WarShortName_2', 'WarShortName_3']), axis=1)
result['WarShortName'] = pd.to_numeric(result['WarShortName'], errors='coerce').fillna(0).astype(int)
result['WarType'] = join_2.apply(lambda r: coalesce_columns(r, ['WarType_0', 'WarType', 'WarType_2', 'WarType_3']), axis=1)
result['WarType'] = pd.to_numeric(result['WarType'], errors='coerce').fillna(0).astype(int)
result['IsIntervention'] = join_2['IsIntervention'].fillna(0).astype(int)

result = result.groupby('IsInternational', as_index=False).agg({
    'WarID': 'max',
    'WarShortName': 'max',
    'WarType': 'max',
    'IsIntervention': 'max'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)