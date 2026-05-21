import pandas as pd
import numpy as np
import os

input_file = "data/raw/TWOSIDES.csv"
output_file = "data/processed/clean_dataset.csv"

def get_severity(prr):
    try:
        val = float(prr)
        if val < 2.0:
            return "Minor"
        elif val < 5.0:
            return "Moderate"
        else:
            return "Major"
    except:
        return np.nan

print("🚀 INITIALIZING MEDGUARD DATA BUILDER (UNIQUE PAIRS ONLY)...")
print(f"📂 Scanning massive raw dataset: {input_file}")

minor_samples = []
moderate_samples = []
major_samples = []

seen_pairs = set()

# The system can comfortably handle ~4,500 unique chemical interactions without hitting API rate limits.
target_per_class = 1500  
chunk_size = 100_000
total_processed = 0

for chunk in pd.read_csv(input_file, chunksize=chunk_size, low_memory=False):
    total_processed += len(chunk)
    
    # Drop completely nasty rows first
    chunk = chunk.dropna(subset=['drug_1_concept_name', 'drug_2_concept_name', 'condition_concept_name', 'PRR'])
    chunk['Severity'] = chunk['PRR'].apply(get_severity)
    chunk = chunk.dropna(subset=['Severity'])

    # Create a unique key for the pair so we don't grab duplicates
    # Since A+B is the same as B+A chemically, we sort them alphabetically to unify them
    chunk['pair_key'] = chunk.apply(lambda row: tuple(sorted([row['drug_1_concept_name'].lower(), row['drug_2_concept_name'].lower()])), axis=1)
    
    # Drop duplicates WITHIN this chunk
    chunk = chunk.drop_duplicates(subset=['pair_key'])
    
    # Filter out anything we've already collected globally across previous chunks
    chunk = chunk[~chunk['pair_key'].isin(seen_pairs)]
    
    # Now separate by class
    minors = chunk[chunk['Severity'] == 'Minor']
    mods = chunk[chunk['Severity'] == 'Moderate']
    majors = chunk[chunk['Severity'] == 'Major']
    
    len_minor = sum(len(df) for df in minor_samples)
    len_mod = sum(len(df) for df in moderate_samples)
    len_maj = sum(len(df) for df in major_samples)
    
    print(f"   [Streaming] Read {total_processed} rows... (Extracted Unique - Min:{len_minor}, Mod:{len_mod}, Maj:{len_maj})")
    
    # Add new valid rows to our lists
    if len_minor < target_per_class and not minors.empty:
        valid_minors = minors.head(target_per_class - len_minor)
        minor_samples.append(valid_minors)
        seen_pairs.update(valid_minors['pair_key'])
        
    if len_mod < target_per_class and not mods.empty:
        valid_mods = mods.head(target_per_class - len_mod)
        moderate_samples.append(valid_mods)
        seen_pairs.update(valid_mods['pair_key'])
        
    if len_maj < target_per_class and not majors.empty:
        valid_majors = majors.head(target_per_class - len_maj)
        major_samples.append(valid_majors)
        seen_pairs.update(valid_majors['pair_key'])

    # Stop once we hit our goal
    len_minor = sum(len(df) for df in minor_samples)
    len_mod = sum(len(df) for df in moderate_samples)
    len_maj = sum(len(df) for df in major_samples)
    if len_minor >= target_per_class and len_mod >= target_per_class and len_maj >= target_per_class:
        break

print("\n🎉 Found enough UNIQUE balanced data! Merging and shuffling...")

df_minors = pd.concat(minor_samples).head(target_per_class)
df_mods = pd.concat(moderate_samples).head(target_per_class)
df_majors = pd.concat(major_samples).head(target_per_class)

final_df = pd.concat([df_minors, df_mods, df_majors])
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

final_csv = pd.DataFrame({
    'Drug_A': final_df['drug_1_concept_name'],
    'Drug_B': final_df['drug_2_concept_name'],
    'Side_Effect': final_df['condition_concept_name'],
    'Severity_Score': final_df['PRR'],
    'Severity': final_df['Severity']
})

final_csv.to_csv(output_file, index=False)
print(f"✅ SUCCESSFULLY SAVED TO {output_file}")
print(f"📊 Matrix Shape: {final_csv.shape[0]} rows × {final_csv.shape[1]} columns")
