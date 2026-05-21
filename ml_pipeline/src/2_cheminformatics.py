import pandas as pd
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
import numpy as np
import time
import os
import socket
import warnings

warnings.filterwarnings('ignore')
socket.setdefaulttimeout(15)

def generate_chemical_features(input_path, output_path):
    print("🧪 INITIALIZING MEDGUARD BIOLOGICAL ENRICHMENT ENGINE (V3)...")
    
    df = pd.read_csv(input_path)
    unique_drugs = pd.concat([df['Drug_A'], df['Drug_B']]).unique()
    print(f"🔍 Found {len(unique_drugs)} unique medications. Fetching structural & biological metadata...\n")
    
    # Dictionary to store both fingerprints and physicochemical props
    drug_data = {}
    
    # Morgan Generator
    mfpgen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=256)
    
    for i, drug in enumerate(unique_drugs):
        # Default fallback values
        data = {
            'fp': [0] * 256,
            'weight': 0.0,
            'tpsa': 0.0,
            'xlogp': 0.0,
            'h_donors': 0,
            'h_acceptors': 0
        }
        
        try:
            # Ping PubChem API for the compound
            compounds = pcp.get_compounds(drug, 'name')
            
            if compounds:
                c = compounds[0]
                
                # 1. Structural Fingerprint (RDKit)
                smiles = c.isomeric_smiles
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    data['fp'] = mfpgen.GetFingerprintAsNumPy(mol).tolist()
                
                # 2. Biological/Physicochemical Properties (PubChem)
                data['weight'] = float(c.molecular_weight) if c.molecular_weight else 0.0
                data['tpsa'] = float(c.tpsa) if c.tpsa else 0.0
                data['xlogp'] = float(c.xlogp) if c.xlogp else 0.0
                data['h_donors'] = int(c.h_bond_donor_count) if c.h_bond_donor_count else 0
                data['h_acceptors'] = int(c.h_bond_acceptor_count) if c.h_bond_acceptor_count else 0
                
            drug_data[drug] = data
            
        except Exception as e:
            print(f"   [!] Error fetching '{drug}': {e}")
            drug_data[drug] = data
            
        if (i + 1) % 10 == 0 or (i + 1) == len(unique_drugs):
            print(f"   [{i + 1}/{len(unique_drugs)}] Processed: {drug}")
            
        time.sleep(0.3)  # Slightly longer pause to avoid getting blocked by PubChem during property fetching

    print("\n🧬 Synthesizing Multi-Modal Feature Matrix...")
    
    # Extract features for A and B
    fp_A = [drug_data[d]['fp'] for d in df['Drug_A']]
    fp_B = [drug_data[d]['fp'] for d in df['Drug_B']]
    
    props_A = []
    props_B = []
    bio_cols = ['weight', 'tpsa', 'xlogp', 'h_donors', 'h_acceptors']
    
    for d in df['Drug_A']:
        props_A.append([drug_data[d][col] for col in bio_cols])
    for d in df['Drug_B']:
        props_B.append([drug_data[d][col] for col in bio_cols])

    # Build DataFrames
    cols_fp_A = [f"A_chem_{i}" for i in range(256)]
    cols_fp_B = [f"B_chem_{i}" for i in range(256)]
    cols_bio_A = [f"A_bio_{c}" for c in bio_cols]
    cols_bio_B = [f"B_bio_{c}" for c in bio_cols]
    
    df_fp_A = pd.DataFrame(fp_A, columns=cols_fp_A, index=df.index)
    df_fp_B = pd.DataFrame(fp_B, columns=cols_fp_B, index=df.index)
    df_bio_A = pd.DataFrame(props_A, columns=cols_bio_A, index=df.index)
    df_bio_B = pd.DataFrame(props_B, columns=cols_bio_B, index=df.index)
    
    final_df = pd.concat([
        df[['Drug_A', 'Drug_B', 'Severity']], 
        df_fp_A, df_fp_B,
        df_bio_A, df_bio_B
    ], axis=1)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)
    
    print(f"\n✅ ENRICHMENT PIPELINE COMPLETE!")
    print(f"📊 Matrix Shape: {final_df.shape[0]} rows × {final_df.shape[1]} columns")

# --- RUN THE SCRIPT ---
input_csv = 'data/processed/clean_dataset.csv'
output_csv = 'data/processed/ml_training_data.csv'

generate_chemical_features(input_csv, output_csv)