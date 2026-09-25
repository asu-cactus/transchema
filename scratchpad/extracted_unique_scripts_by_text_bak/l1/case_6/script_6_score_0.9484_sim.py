import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

melted = df0.melt(
    id_vars=['provider_id', 'provider_name', 'provider_zip_code'],
    value_vars=['average_covered_charges', 'average_total_payments', 'average_medicare_payments'],
    var_name='charge_type',
    value_name='charge_value'
)

pivoted = melted.pivot_table(
    index=['provider_id', 'provider_name', 'provider_zip_code'],
    columns='charge_type',
    values='charge_value',
    aggfunc='mean'
).reset_index()

pivoted.columns.name = None

pivoted['provider_id'] = pivoted['provider_id'].astype(int)
pivoted['provider_name'] = pivoted['provider_name'].astype(str)
pivoted['provider_zip_code'] = pivoted['provider_zip_code'].astype(int)
pivoted['average_covered_charges'] = pivoted['average_covered_charges'].astype(float)
pivoted['average_total_payments'] = pivoted['average_total_payments'].astype(float)
pivoted['average_medicare_payments'] = pivoted['average_medicare_payments'].astype(float)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)