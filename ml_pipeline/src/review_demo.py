import pandas as pd
import numpy as np
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
import joblib
import shap
import warnings
import time
import socket

# Hide warnings for a clean presentation
warnings.filterwarnings('ignore')
socket.setdefaulttimeout(10)

def fetch_chemistry(drug_name):
    """Pings PubChem and generates a 256-bit mathematical fingerprint"""
    mfpgen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=256)
    try:
        compound = pcp.get_compounds(drug_name, 'name')
        if compound:
            mol = Chem.MolFromSmiles(compound[0].isomeric_smiles)
            if mol:
                return mfpgen.GetFingerprintAsNumPy(mol).tolist()
    except:
        pass
    return [0] * 256 

def explainable_clinical_check(drug_a, drug_b):
    print("\n" + "="*75)
    print(f"🏥 MEDGUARD - INTERACTION CHECK")
    print(f"   Patient Medication: [ {drug_a.upper()} ] + [ {drug_b.upper()} ]")
    print("="*75)
    
    try:
        db = pd.read_csv('data/processed/clean_dataset.csv')
        match = db[(db['Drug_A'].str.lower() == drug_a.lower()) & (db['Drug_B'].str.lower() == drug_b.lower())]
        if not match.empty:
            known_side_effect = match.iloc[0]['Side_Effect']
        else:
            known_side_effect = "Not in Historical Database (Algorithmic Extrapolation)"
    except:
        known_side_effect = "Database Offline"

    time.sleep(1)
    print("\n[1/4] Loading Trained Machine Learning Engine...")
    try:
        model = joblib.load('models/rf_medguard_model.pkl')
        encoder = joblib.load('models/label_encoder.pkl')
        background_data = pd.read_csv('data/processed/ml_training_data.csv').drop(columns=['Drug_A', 'Drug_B', 'Severity']).sample(50, random_state=42)
    except Exception as e:
        print("❌ Error: Could not find models! Are you in the ml_pipeline folder?")
        return

    time.sleep(1)
    print(f"[2/4] Extracting Chemical Fingerprints...")
    fp_a = fetch_chemistry(drug_a)
    fp_b = fetch_chemistry(drug_b)
    
    cols_A = [f"A_chem_{i}" for i in range(256)]
    cols_B = [f"B_chem_{i}" for i in range(256)]
    input_data = pd.DataFrame([fp_a + fp_b], columns=cols_A + cols_B)

    time.sleep(1)
    print("[3/4] Model Analyzing Structural Conflicts...\n")
    
    prediction_encoded = model.predict(input_data)[0]
    severity = encoder.inverse_transform([prediction_encoded])[0]
    confidence = max(model.predict_proba(input_data)[0]) * 100

    time.sleep(1)
    print("[4/4] Generating SHAP Reasoning Weights...")
    explainer = shap.TreeExplainer(model, background_data, feature_perturbation='interventional')
    shap_values = explainer.shap_values(input_data)
    
    class_index = list(model.classes_).index(prediction_encoded)
    
    if isinstance(shap_values, list): 
        pred_shap_values = shap_values[class_index][0]
    else: 
        pred_shap_values = shap_values[0, :, class_index]
        
    feature_names = input_data.columns
    feature_impacts = list(zip(feature_names, pred_shap_values))
    feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)

    print("\n" + "="*75)
    print("🩺 SYSTEM RECOMMENDATION & EXPLANATION:")
    print("="*75)
    
    print(f"🦠 Known Clinical History : {known_side_effect.upper()}")

    if severity == 'Major':
        print(f"🚨 ALERT                  : {severity.upper()} INTERACTION DETECTED")
        print(f"   Model Confidence       : {confidence:.1f}%")
        print("   Action                 : High risk of adverse reaction. Consider alternative therapy.")
    elif severity == 'Moderate':
        print(f"⚠️ WARNING                : {severity.upper()} INTERACTION DETECTED")
        print(f"   Model Confidence       : {confidence:.1f}%")
        print("   Action                 : Monitor patient closely for side effects.")
    else:
        print(f"✅ SAFE                   : {severity.upper()} / NO SEVERE INTERACTION")
        print(f"   Model Confidence       : {confidence:.1f}%")
        print("   Action                 : Safe to prescribe.")

    print("\n📊 MODEL REASONING (Why did the classifier choose this?):")
    print("   The following chemical properties influenced the model's decision:")
    for feature, impact in feature_impacts[:3]: 
        direction = "Increased" if impact > 0 else "Decreased"
        clean_feature_name = feature.replace('B_chem_', 'Drug B - Chemical Feature ').replace('A_chem_', 'Drug A - Chemical Feature ')
        print(f"   - {clean_feature_name}: {direction} the severity risk (SHAP weight: {impact:+.4f})")
        
    print("="*75 + "\n")


# --- LIVE TERMINAL DEMO INTERFACE ---
if __name__ == "__main__":
    print("\n" + "*"*75)
    print("🚀 MEDGUARD - LIVE INTERACTIVE TERMINAL")
    print("Type 'exit' or 'quit' at any time to shut down the engine.")
    print("*"*75)

    while True:
        drug_1 = input("\n💊 Enter Patient's Current Medication (Drug A) : ").strip()
        if drug_1.lower() in ['exit', 'quit']:
            print("Shutting down MedGuard. Goodbye!")
            break
            
        drug_2 = input("💊 Enter Proposed Medication (Drug B)        : ").strip()
        if drug_2.lower() in ['exit', 'quit']:
            print("Shutting down MedGuard. Goodbye!")
            break
            
        if drug_1 and drug_2:
            explainable_clinical_check(drug_1, drug_2)
        else:
            print("⚠️ Please enter valid drug names.")