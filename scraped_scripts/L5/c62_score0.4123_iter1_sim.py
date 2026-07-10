import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_62/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

def convert_age_group(age_str):
    if isinstance(age_str, str) and age_str.lower().startswith("age "):
        parts = age_str.split()
        for part in parts:
            if part.isdigit():
                return int(part)
        # fallback: try to extract first number in the string
        import re
        m = re.search(r'\d+', age_str)
        if m:
            return int(m.group())
    elif pd.api.types.is_integer(age_str):
        return age_str
    return pd.NA

df["Age Group"] = df["Age Group"].apply(convert_age_group)

df = df.astype({
    "Sex": "string",
    "Age Group": "Int64",
    "Don't know/Refused/Missing": "Int64",
    "Normal Weight": "Int64",
    "Obese": "Int64",
    "Overweight": "Int64",
    "Underweight": "Int64"
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_62/target_multisource_mcts.csv", index=False)