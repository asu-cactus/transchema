import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

unpivoted = source1.melt(id_vars=['Student ID', 'student_name', 'gender', 'grade', 'school_name'],
                         value_vars=['reading_score', 'math_score'],
                         var_name='a', value_name='b')
unpivoted['a'] = unpivoted['a'].map({'reading_score': 'reading_score', 'math_score': 'math_score'})

joined = pd.merge(source0, unpivoted, on='school_name', how='inner')

agg = joined.groupby(['school_name', 'type'], as_index=False).agg(
    b=('b', 'sum'),
    c=('size', 'sum'),
    d=('budget', 'mean'),
    e=('a', lambda x: x.map({'reading_score': 0, 'math_score': 1}).mul(joined.loc[x.index, 'b']).mean())
)

agg['a'] = agg['type']
agg = agg[['school_name', 'a', 'b', 'c', 'd', 'e']]

agg['a'] = agg['a'].astype(str)
agg['b'] = agg['b'].astype(int)
agg['c'] = agg['c'].astype(int)
agg['d'] = agg['d'].astype(float)
agg['e'] = agg['e'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)