import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

def top2_businesses(group):
    top2 = group.nlargest(2, 'counts')
    result = {}
    if len(top2) > 0:
        result['businesses_x'] = top2.iloc[0]['businesses']
        result['counts_x'] = int(top2.iloc[0]['counts'])
    else:
        result['businesses_x'] = None
        result['counts_x'] = None
    if len(top2) > 1:
        result['businesses_y'] = top2.iloc[1]['businesses']
        result['counts_y'] = int(top2.iloc[1]['counts'])
    else:
        result['businesses_y'] = None
        result['counts_y'] = None
    return pd.Series(result)

def top2_businesses_next3(group):
    sorted_group = group.sort_values('counts', ascending=False)
    next3 = sorted_group.iloc[2:5]
    result = {}
    if len(next3) > 0:
        result['businesses_x_5'] = next3.iloc[0]['businesses']
        result['counts_x_6'] = int(next3.iloc[0]['counts'])
    else:
        result['businesses_x_5'] = None
        result['counts_x_6'] = None
    if len(next3) > 1:
        result['businesses_y_7'] = next3.iloc[1]['businesses']
        result['counts_y_8'] = int(next3.iloc[1]['counts'])
    else:
        result['businesses_y_7'] = None
        result['counts_y_8'] = None
    return pd.Series(result)

grouped = df_all.groupby('zipcode')

top2 = grouped.apply(top2_businesses)
next3 = grouped.apply(top2_businesses_next3)

result = pd.concat([top2, next3], axis=1).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv", index=False)