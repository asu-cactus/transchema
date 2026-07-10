import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_29/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['school_name'], value_vars=['reading_score', 'math_score'], 
                      var_name='subject', value_name='score')

df_math = df_unpivot[df_unpivot['subject'] == 'math_score'][['school_name', 'score']]

df_math = df_math.rename(columns={'score': 'math_score'})

df_math['math_score'] = df_math['math_score'].astype(float)

df_math.to_csv("autopipeline-benchmarks/github-pipelines/length5_29/target_multisource_mcts.csv", index=False)