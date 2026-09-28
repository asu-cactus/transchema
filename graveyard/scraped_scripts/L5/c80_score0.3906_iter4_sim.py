import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

df0['Gender'] = df0['Gender'].astype('category').cat.codes

agg = df0.groupby('Gender').agg(
    Purchase_ID_count=('Purchase ID', 'count'),
    Price_sum=('Price', 'sum'),
    Age_avg=('Age', 'mean')
).reset_index()

agg['Purchase_ID_count'] = agg['Purchase_ID_count'].astype(int)
agg['Price_sum'] = agg['Price_sum'].astype(float)
agg['Age_avg'] = agg['Age_avg'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)