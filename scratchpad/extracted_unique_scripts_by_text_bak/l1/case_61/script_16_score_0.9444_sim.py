import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

df_joined = df.merge(df, on="provider_id", suffixes=('_left', '_right'))

df_unpivot = pd.melt(df_joined,
                     id_vars=['provider_id', 'provider_name_left', 'provider_zip_code_left'],
                     value_vars=['average_covered_charges_left', 'average_total_payments_left', 'average_medicare_payments_left'],
                     var_name='charge_type',
                     value_name='charge_value')

df_pivot = df_unpivot.pivot_table(index=['provider_id', 'provider_name_left', 'provider_zip_code_left'],
                                  columns='charge_type',
                                  values='charge_value',
                                  aggfunc='mean').reset_index()

df_pivot.columns.name = None

df_result = df_pivot.rename(columns={
    'provider_name_left': 'provider_name',
    'provider_zip_code_left': 'provider_zip_code',
    'average_covered_charges_left': 'average_covered_charges',
    'average_total_payments_left': 'average_total_payments',
    'average_medicare_payments_left': 'average_medicare_payments'
})

df_result['provider_id'] = df_result['provider_id'].astype(int)
df_result['provider_zip_code'] = df_result['provider_zip_code'].astype(int)
df_result['provider_name'] = df_result['provider_name'].astype(str)
df_result['average_covered_charges'] = df_result['average_covered_charges'].astype(float)
df_result['average_total_payments'] = df_result['average_total_payments'].astype(float)
df_result['average_medicare_payments'] = df_result['average_medicare_payments'].astype(float)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)