import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

melted = df0.melt(
    id_vars=['provider_id', 'provider_name', 'provider_zip_code'],
    value_vars=['average_covered_charges', 'average_total_payments', 'average_medicare_payments'],
    var_name='charge_type',
    value_name='charge_value'
)

agg = melted.groupby(['provider_id', 'provider_name', 'provider_zip_code', 'charge_type'], as_index=False)['charge_value'].mean()

pivot = agg.pivot_table(
    index=['provider_id', 'provider_name', 'provider_zip_code'],
    columns='charge_type',
    values='charge_value'
).reset_index()

pivot.columns.name = None

pivot = pivot.rename(columns={
    'average_covered_charges': 'average_covered_charges',
    'average_total_payments': 'average_total_payments',
    'average_medicare_payments': 'average_medicare_payments'
})

pivot['provider_id'] = pivot['provider_id'].astype(int)
pivot['provider_zip_code'] = pivot['provider_zip_code'].astype(int)
pivot['provider_name'] = pivot['provider_name'].astype(str)
pivot['average_covered_charges'] = pivot['average_covered_charges'].astype(float)
pivot['average_total_payments'] = pivot['average_total_payments'].astype(float)
pivot['average_medicare_payments'] = pivot['average_medicare_payments'].astype(float)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)