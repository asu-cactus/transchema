import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv", index_col=0)

grouped_source1 = source1.groupby('Rank', as_index=False).agg({
    'Documents': 'sum',
    'Citable documents': 'sum',
    'Citations': 'sum',
    'Self-citations': 'sum',
    'Citations per document': 'mean',
    'H index': 'max',
    'Country': 'first'
})

joined_12 = pd.merge(grouped_source1, source2, how='inner', left_on='Country', right_on='Country')

source0_2006_2015 = source0[['Country Name'] + [str(y) for y in range(2006, 2016)]].copy()
source0_2006_2015.rename(columns={'Country Name': 'Country'}, inplace=True)

final_join = pd.merge(joined_12, source0_2006_2015, how='inner', left_on='Country', right_on='Country')

final_join.rename(columns={
    'Country': 'Country',
    'Rank': 'Rank',
    'Documents': 'Documents',
    'Citable documents': 'Citable documents',
    'Citations': 'Citations',
    'Self-citations': 'Self-citations',
    'Citations per document': 'Citations per document',
    'H index': 'H index',
    'Energy Supply': 'Energy Supply',
    'Energy Supply per Capita': 'Energy Supply per Capita',
    '% Renewable': '% Renewable'
}, inplace=True)

cols_order = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index',
              'Energy Supply', 'Energy Supply per Capita', '% Renewable'] + [str(y) for y in range(2006, 2016)]

result = final_join[cols_order]

for col in ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index',
            'Energy Supply', 'Energy Supply per Capita', '% Renewable'] + [str(y) for y in range(2006, 2016)]:
    result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv", index=False)