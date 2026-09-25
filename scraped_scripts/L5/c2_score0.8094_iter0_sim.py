import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

def group_source(df):
    return df.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()

g0 = group_source(source0)
g2 = group_source(source2)
g4 = group_source(source4)
g3 = group_source(source3)

j02 = pd.merge(g0, g2, on='zipcode', suffixes=('_x', '_y'))
j024 = pd.merge(j02, g4, on='zipcode')
j024 = j024.rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})
j0243 = pd.merge(j024, g3, on='zipcode')
j0243 = j0243.rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})

j_all = pd.merge(j0243, source1, on='zipcode')
j_all = pd.merge(j_all, source5, on='zipcode')

agg = j_all.groupby(['zipcode', 'boro'], as_index=False).agg({
    'businesses_x': 'first',
    'counts_x': 'sum',
    'businesses_y': 'first',
    'counts_y': 'sum',
    'businesses_x_5': 'first',
    'counts_x_6': 'sum',
    'businesses_y_7': 'first',
    'counts_y_8': 'sum',
    'boro': 'first',
    'businesses': 'sum'
})

agg = agg[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)