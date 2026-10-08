import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

join_03 = pd.merge(
    s0,
    s3,
    how='inner',
    left_on=['WarID', 'PolityID', 'StartYear'],
    right_on=['WarID', 'PolityID', 'StartYear'],
    suffixes=('_0', '_3')
)

union_012 = pd.concat([s0, s1, s2], ignore_index=True, sort=False)

final = pd.merge(
    union_012,
    join_03,
    how='inner',
    left_on=['WarID', 'PolityID', 'StartYear'],
    right_on=['WarID', 'PolityID', 'StartYear'],
    suffixes=('', '_join')
)

cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

result = final[cols]

for c in ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']:
    if result[c].dtype == 'O':
        try:
            result[c] = pd.to_numeric(result[c], errors='ignore')
        except:
            pass

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)