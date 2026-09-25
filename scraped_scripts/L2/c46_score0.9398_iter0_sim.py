import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_46/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df.astype({
    'adm0_name': str,
    'adm1_name': str,
    'mkt_name': str,
    'cm_name': str,
    'cur_name': str,
    'pt_name': str,
    'um_id': 'Int64',
    'um_name': str,
    'mp_month': 'Int64',
    'mp_year': 'Int64',
    'mp_price': float
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_46/target_multisource_mcts.csv", index=False)