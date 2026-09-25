import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_65/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_65/training_1.csv", index_col=0)

unpivot = source1.melt(id_vars=['Mouse ID', 'Timepoint', 'Metastatic Sites'], 
                       value_vars=['Tumor Volume (mm3)'], 
                       var_name='Drug', value_name='Tumor Volume')
unpivot['Drug'] = unpivot['Drug'].str.replace('Tumor Volume (mm3)', '').str.strip()

joined = pd.merge(unpivot, source0, on=['Mouse ID', 'Drug'], how='inner')

grouped = joined.groupby(['Timepoint', 'Drug'], as_index=False)['Tumor Volume'].mean()

pivoted = grouped.pivot(index='Timepoint', columns='Drug', values='Tumor Volume')

pivoted.columns = pivoted.columns.str.strip()

pivoted = pivoted.rename(columns={
    'Capomulin': 'Capomulin',
    'Ceftamin': 'Ceftamin',
    'Infubinol': 'Infubinol',
    'Ketapril': 'Ketapril',
    'Naftisol': 'Naftisol',
    'Placebo': 'Placebo',
    'Propriva': 'Propriva',
    'Ramicane': 'Ramicane',
    'Stelasyn': 'Stelasyn',
    'Zoniferol': 'Zoniferol'
})

result = pivoted.reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_65/target_multisource_mcts.csv", index=False)