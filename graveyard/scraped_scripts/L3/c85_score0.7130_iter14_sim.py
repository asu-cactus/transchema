import pandas as pd
import numpy as np

def parse_money(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        x = x.strip()
        if x == 'NR' or x == '':
            return np.nan
        return float(x.replace('$','').replace(',',''))
    return float(x)

s0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv', index_col=0)
s1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv', index_col=0)
s2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv', index_col=0)
s3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv', index_col=0)

s0['m1403'] = s0['m1403'].apply(parse_money)
s1['m1402'] = s1['m1402'].apply(parse_money)
s2['m1401'] = s2['m1401'].apply(parse_money)

agg_s2 = s2.groupby(['County', 'm1401'], as_index=False).agg({'m1401':'sum'})
agg_s0 = s0.groupby('County', as_index=False).agg({'m1403':'sum'})

# The partial plan suggests summing Source3_85_2.m1401 and Source3_85_0.m1403 grouped by County and m1401,
# but m1401 is a value column, not a grouping key. We interpret the plan as summing m1401 and m1403 per County.

# Since s2 has County and m1401, and s0 has County and m1403, we join on County and sum the values.

# Join aggregated s2 and s0 on County
join_0 = pd.merge(agg_s2[['County', 'm1401']], agg_s0, on='County', how='outer')

# Join with s1 on County to bring in m1402 if needed (though target schema does not include m1402)
join_1 = pd.merge(join_0, s1[['County', 'm1402']], on='County', how='outer')

# Join with s3 on County (s3 only has County)
join_2 = pd.merge(join_1, s3[['County']], on='County', how='outer')

# Final target schema: ['County': string, 'm1401': string, 'm1403': string]
# Convert m1401 and m1403 back to string with $ and commas, fill NaN with 'NR'

def format_money(x):
    if pd.isna(x):
        return 'NR'
    return '${:,.0f}'.format(x)

result = join_2[['County', 'm1401', 'm1403']].copy()
result['m1401'] = result['m1401'].apply(format_money)
result['m1403'] = result['m1403'].apply(format_money)

result.to_csv('autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv', index=False)