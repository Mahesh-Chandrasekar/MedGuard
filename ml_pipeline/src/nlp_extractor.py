import pandas as pd
import re
import time
import warnings

warnings.filterwarnings('ignore')

def build_lexical_knowledge_base():
    """Loads all known drugs from your existing TWOSIDES dataset"""
    try:
        # We use the dataset you already cleaned!
        df = pd.read_csv('data/processed/clean_dataset.csv')
        # Combine Drug_A and Drug_B columns to get every unique drug in the database
        all_drugs = set(df['Drug_A'].str.lower()).union(set(df['Drug_B'].str.lower()))
        return all_drugs
    except FileNotFoundError:
        print("⚠️ Could not find clean_dataset.csv. Using fallback dictionary.")
        return {"aspirin", "warfarin", "ibuprofen", "acetaminophen", "glycopyrronium"}

def extract_drugs_from_notes(clinical_text, known_drugs):
    print("\n" + "="*80)
    print("📄 SCANNING CLINICAL NOTES (Lexical NLP Pipeline)")
    print("="*80)
    print(f"Raw Text: \"{clinical_text}\"\n")
    time.sleep(1)
    
    extracted_drugs = set()
    text_lower = clinical_text.lower()
    
    # Smart scanning using Regular Expressions (Regex)
    for drug in known_drugs:
        # \b ensures we only match whole words (so "in" doesn't match inside "aspirin")
        pattern = r'\b' + re.escape(drug) + r'\b'
        
        # If the exact drug name is found in the text, add it to our extracted list
        if re.search(pattern, text_lower):
            extracted_drugs.add(drug)
            
    drug_list = list(extracted_drugs)
    
    print("🔬 EXTRACTION RESULTS:")
    if len(drug_list) > 0:
        print(f"   ✅ Found {len(drug_list)} Medications: {drug_list}")
    else:
        print("   ⚠️ No medications detected in the text.")
        
    print("="*80 + "\n")
    return drug_list

if __name__ == "__main__":
    print("🧠 Initializing Lexical NLP Engine...")
    knowledge_base = build_lexical_knowledge_base()
    print(f"📚 Loaded {len(knowledge_base)} unique medications into memory.")
    
    # A messy, real-world doctor's note for testing
    sample_note = "Patient was admitted for atrial fibrillation. Has a history of taking 81mg of aspirin and ibuprofen for joint pain. Started taking warfarin yesterday."
    
    # Run the extractor
    found_meds = extract_drugs_from_notes(sample_note, knowledge_base)