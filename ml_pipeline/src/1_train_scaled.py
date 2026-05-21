import pandas as pd
import numpy as np
import xgboost as xgb
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
import joblib
import warnings
import os
from tqdm import tqdm
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

warnings.filterwarnings('ignore')

CHUNK_SIZE = 50000  
RAW_DATA_PATH = 'data/raw/twosides.csv' 
CACHE_PATH = 'data/processed/chem_cache.joblib'
# --- THE NEW SAFETY LIMIT ---
MAX_ROWS = 1_000_000 # Stop at 1 Million rows to protect RAM

print("="*80)
print("🚀 MEDGUARD ENTERPRISE: LARGE-SCALE MODEL TRAINING")
print(f"⚠️  MEMORY CAP SET TO: {MAX_ROWS:,} ROWS")
print("="*80)

def get_fingerprint(drug_name, cache):
    if drug_name in cache: return cache[drug_name]
    mfpgen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=256)
    try:
        compound = pcp.get_compounds(drug_name, 'name')
        if compound:
            mol = Chem.MolFromSmiles(compound[0].isomeric_smiles)
            if mol:
                fp = mfpgen.GetFingerprintAsNumPy(mol).tolist()
                cache[drug_name] = fp
                return fp
    except: pass
    cache[drug_name] = [0] * 256
    return [0] * 256

if os.path.exists(CACHE_PATH):
    print("📚 Loading existing chemical fingerprint cache...")
    chem_cache = joblib.load(CACHE_PATH)
else:
    chem_cache = {}

print("\n⚙️ Processing Dataset...")
processed_features = []
processed_labels = []
total_processed = 0

try:
    for chunk in tqdm(pd.read_csv(RAW_DATA_PATH, chunksize=CHUNK_SIZE)):
        for _, row in chunk.iterrows():
            drug_a = str(row['drug_1_concept_name'])
            drug_b = str(row['drug_2_concept_name'])
            
            if row['PRR'] == 'PRR' or drug_a == 'drug_1_concept_name': continue
            prr_raw = row['PRR']
            if pd.isna(prr_raw): continue 
            
            try:
                prr_score = float(prr_raw)
            except ValueError: continue 

            if prr_score >= 2.0: severity = 'Major'
            elif prr_score >= 1.2: severity = 'Moderate'
            else: severity = 'Minor'

            fp_a = get_fingerprint(drug_a, chem_cache)
            fp_b = get_fingerprint(drug_b, chem_cache)
            
            processed_features.append(fp_a + fp_b)
            processed_labels.append(severity)
            
        joblib.dump(chem_cache, CACHE_PATH)
        
        # --- THE SAFETY BRAKE ---
        total_processed += len(chunk)
        if total_processed >= MAX_ROWS:
            print(f"\n🛑 Reached safe memory limit of {MAX_ROWS:,} rows. Stopping extraction...")
            break

except FileNotFoundError:
    print(f"❌ ERROR: Could not find {RAW_DATA_PATH}.")
    exit()

print("\n🧬 Encoding Labels & Splitting Data...")
encoder = LabelEncoder()
encoded_labels = encoder.fit_transform(processed_labels)
joblib.dump(encoder, 'models/label_encoder.pkl')

cols_A = [f"A_chem_{i}" for i in range(256)]
cols_B = [f"B_chem_{i}" for i in range(256)]
X = pd.DataFrame(processed_features, columns=cols_A + cols_B)
y = encoded_labels

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n🧠 Training Extreme Gradient Boosting (XGBoost) Model...")
xgb_model = xgb.XGBClassifier(
    n_estimators=150,
    learning_rate=0.05,
    max_depth=6,
    n_jobs=-1,
    random_state=42
)

xgb_model.fit(X_train, y_train)
accuracy = xgb_model.score(X_test, y_test)
print(f"\n✅ Training Complete! Model Accuracy: {accuracy * 100:.2f}%")
joblib.dump(xgb_model, 'models/xgb_medguard_model.pkl')
print("💾 Production Model saved as 'xgb_medguard_model.pkl'")
print("="*80)