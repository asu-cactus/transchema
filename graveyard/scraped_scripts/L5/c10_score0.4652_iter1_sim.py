import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_10/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['school_name'], value_vars=['reading_score', 'math_score'], 
                      var_name='score_type', value_name='score_value')

df_reading = df_unpivot[df_unpivot['score_type'] == 'reading_score']

result = df_reading[['school_name', 'score_value']].rename(columns={'score_value': 'reading_score'})

result['reading_score'] = result['reading_score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_10/target_multisource_mcts.csv", index=False)