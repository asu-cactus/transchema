import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv", index_col=0)

joined = pd.merge(src0, src2, on="WarID", suffixes=('_0', '_2'))

result = pd.DataFrame()
result['Outcome'] = joined['Outcome_0'].astype('Int64')
result['WarID'] = joined['WarID'].astype('Int64')

def to_int64_or_na(series):
    try:
        return series.astype('Int64')
    except:
        return series

result['PolityName'] = to_int64_or_na(joined['PolityName_0'])
result['StartYear'] = to_int64_or_na(joined['StartYear_0'])
result['StartMonth'] = to_int64_or_na(joined['StartMonth_0'])
result['StartDay'] = to_int64_or_na(joined['StartDay_0'])
result['EndYear'] = to_int64_or_na(joined['EndYear_0'])
result['EndMonth'] = to_int64_or_na(joined['EndMonth_0'])
result['EndDay'] = to_int64_or_na(joined['EndDay_0'])
result['Initiator'] = to_int64_or_na(joined['Initiator_0'])
result['Deaths'] = to_int64_or_na(joined['Deaths_0'])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)