import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

df0['production_countries_str'] = df0['production_countries'].astype(str)
df0['spoken_languages_str'] = df0['spoken_languages'].astype(str)

grouped = df0.groupby(
    ['original_language', 'production_countries_str', 'spoken_languages_str', 'status'],
    dropna=False,
    as_index=False
).agg(
    year_min=('year', 'min'),
    year_max=('year', 'max'),
    vote_count_avg=('vote_count', 'mean')
)

result = pd.DataFrame()
result['year'] = grouped['year_min'].astype(int)
result['0'] = grouped['vote_count_avg'].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)