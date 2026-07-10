import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

agg0 = source0.groupby(['school_name', 'type'], as_index=False).agg({'size':'sum', 'budget':'sum'})
joined = pd.merge(agg0, source1, on='school_name', how='inner')
agg1 = joined.groupby(['school_name', 'type'], as_index=False).agg({'reading_score':'mean', 'math_score':'mean'})

result = pd.DataFrame()
result['school_name'] = agg1['school_name']
result['a'] = agg1['type']
result['b'] = agg0.set_index(['school_name', 'type']).loc[result.set_index(['school_name', 'a']).index, 'size'].values.astype(int)
result['c'] = agg0.set_index(['school_name', 'type']).loc[result.set_index(['school_name', 'a']).index, 'budget'].values.astype(int)
result['d'] = agg1['reading_score'].astype(float)
result['e'] = agg1['math_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)