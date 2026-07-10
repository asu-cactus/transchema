import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_13/training_2.csv", index_col=0)

s1_renamed = s1.rename(columns={"COD_AREANEGO": "COD_AREANEGO", "COD_EDAD": "COD_EDAD", "estado_cli": "estado_cli", "COD_PERSONA": "COD_PERSONA"})
s2_renamed = s2.rename(columns={"cod_areanego": "COD_AREANEGO"})

s2_sub = s2_renamed[["COD_OFICI", "COD_AREANEGO", "COD_EDAD"]] if "COD_EDAD" in s2_renamed.columns else s2_renamed[["COD_OFICI", "COD_AREANEGO"]]
# Actually s2 does not have COD_EDAD or COD_PERSONA, so union with s1 is not possible directly.
# The partial plan says UNION : [Source4_13_1, Source4_13_2], but schemas differ.
# So we must check columns carefully.

# Check columns of s1 and s2:
# s1 columns: ['COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'estado_cli']
# s2 columns: ['COD_OFICI', 'COD_NIVELOFIC', 'des_ofici', 'cod_cbc', 'des_cbc', 'cod_zona', 'des_zona', 'COD_TERRIT', 'des_territ', 'cod_areanego', 'des_areanego']

# They differ, so UNION is not possible directly.
# The partial plan says UNION : [Source4_13_1, Source4_13_2], so we must interpret that as union on common columns only.

# The only common columns are cod_areanego (s2) and COD_AREANEGO (s1), but s2 has no COD_PERSONA or estado_cli or COD_EDAD.

# So the partial plan is likely a hint to union s1 and s2 after selecting columns to match target schema.

# But s2 does not have COD_PERSONA, estado_cli, or COD_EDAD, so union is impossible.

# So the best is to union s1 and s2 after renaming cod_areanego to COD_AREANEGO and filling missing columns with NaN.

s2_sub = s2.rename(columns={"cod_areanego": "COD_AREANEGO"})
s2_sub = s2_sub.assign(COD_PERSONA=pd.NA, COD_EDAD=pd.NA, estado_cli=pd.NA)
s2_sub = s2_sub[["COD_PERSONA", "COD_AREANEGO", "COD_EDAD", "estado_cli"]]

s1_sub = s1[["COD_PERSONA", "COD_AREANEGO", "COD_EDAD", "estado_cli"]]

union_df = pd.concat([s1_sub, s2_sub], ignore_index=True)

# Now join union_df with s0 on COD_PERSONA to get COD_INTERV from s0
s0_sub = s0[["COD_PERSONA", "COD_INTERV"]]

joined = pd.merge(union_df, s0_sub, on="COD_PERSONA", how="left")

# Reorder columns to target schema: ['COD_INTERV', 'estado_cli', 'COD_PERSONA', 'COD_AREANEGO', 'COD_EDAD']
result = joined[["COD_INTERV", "estado_cli", "COD_PERSONA", "COD_AREANEGO", "COD_EDAD"]]

# Fix data types
result["COD_INTERV"] = result["COD_INTERV"].astype("string")
result["estado_cli"] = result["estado_cli"].astype("string")
result["COD_PERSONA"] = pd.to_numeric(result["COD_PERSONA"], errors="coerce").astype("Int64")
result["COD_AREANEGO"] = pd.to_numeric(result["COD_AREANEGO"], errors="coerce").astype("Int64")
result["COD_EDAD"] = pd.to_numeric(result["COD_EDAD"], errors="coerce").astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_13/target_multisource_mcts.csv", index=False)