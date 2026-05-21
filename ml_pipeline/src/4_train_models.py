import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# --- Import the 4 ML Competitors ---
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

def compute_interaction_features(df):
    """Adds Tanimoto Similarity and structural delta between Drug A and Drug B"""
    print("🧪 ENGINEERING INTERACTION SYMMETRY (Tanimoto & Structural Delta)...")
    
    cols_A = [f"A_chem_{i}" for i in range(256)]
    cols_B = [f"B_chem_{i}" for i in range(256)]
    
    # Extract fingerprints as matrices
    fp_A = df[cols_A].values
    fp_B = df[cols_B].values
    
    # 1. Tanimoto Coefficient: (A ∩ B) / (A ∪ B)
    intersection = np.sum(np.logical_and(fp_A, fp_B), axis=1)
    union = np.sum(np.logical_or(fp_A, fp_B), axis=1)
    
    # Avoid division by zero
    tanimoto = np.divide(intersection, union, out=np.zeros_like(intersection, dtype=float), where=union!=0)
    df['Interaction_Tanimoto'] = tanimoto
    
    # 2. Structural Delta (Absolute Difference)
    # This helps the model see motifs that are present in one but not the other
    delta_fp = np.abs(fp_A - fp_B)
    delta_cols = [f"Delta_chem_{i}" for i in range(256)]
    df_delta = pd.DataFrame(delta_fp, columns=delta_cols, index=df.index)
    
    # 3. Physicochemical Deltas (Bio-Interaction Logic)
    bio_props = ['weight', 'tpsa', 'xlogp', 'h_donors', 'h_acceptors']
    for prop in bio_props:
        df[f'Delta_bio_{prop}'] = np.abs(df[f'A_bio_{prop}'] - df[f'B_bio_{prop}'])
    
    return pd.concat([df, df_delta], axis=1)

def run_comparative_analysis(data_path, model_dir):
    print("🧠 INITIALIZING MEDGUARD AI ADVANCED RESEARCH ANALYSER (V3.5)...\n")
    
    # 1. Load Data
    print("📂 Loading biological & chemical feature matrix...")
    df = pd.read_csv(data_path)
    
    # 2. Advanced Feature Engineering (The path to 80%!)
    df_enriched = compute_interaction_features(df)
    
    # Drop identifying columns and target
    X = df_enriched.drop(columns=['Drug_A', 'Drug_B', 'Severity'])
    y_raw = df_enriched['Severity']
    
    # 3. Encode Labels
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    # 4. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 5. Apply SMOTE to the Training Data
    print("⚖️ Applying SMOTE to balance the clinical severity classes...")
    smote = SMOTE(random_state=42)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    
    # Scale features (Critical for SVM and LR)
    print("📏 Scaling multi-modal features for optimal convergence...")
    scaler = StandardScaler()
    X_train_balanced = scaler.fit_transform(X_train_balanced)
    X_test_scaled = scaler.transform(X_test)
    
    # 6. Define the 4 Ttuned Models
    models = {
        "Logistic Regression (Baseline)": (
            LogisticRegression(max_iter=2000, random_state=42),
            {'C': [0.1, 1.0, 10.0]}
        ),
        "Support Vector Machine (SVM)": (
            SVC(probability=True, random_state=42),
            {'kernel': ['rbf'], 'C': [1.0, 10.0], 'gamma': ['scale']} 
        ),
        "Random Forest": (
            RandomForestClassifier(random_state=42, n_jobs=-1),
            {'n_estimators': [200, 300], 'max_depth': [15, 25]}
        ),
        "XGBoost": (
            XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss', n_jobs=-1),
            {'n_estimators': [200, 300], 'learning_rate': [0.05, 0.1], 'max_depth': [6, 9]}
        )
    }
    
    results = {}
    best_model_name = ""
    best_accuracy = 0
    best_model = None

    print("\n🏁 STARTING THE ALGORITHM RACE (ULTRA-ENRICHED DATASET)...\n")
    
    # 7. Train, Tune and Evaluate each model
    for name, (model, params) in models.items():
        print(f"⚙️ Tuning & Training {name}...")
        
        grid = GridSearchCV(model, params, cv=3, scoring='accuracy', n_jobs=-1)
        grid.fit(X_train_balanced, y_train_balanced)
        
        best_tuned_model = grid.best_estimator_
        y_pred = best_tuned_model.predict(X_test_scaled)
        acc = accuracy_score(y_test, y_pred)
        
        results[name] = acc
        print(f"   🏆 Accuracy: {acc * 100:.2f}%")
        print(f"   🔧 Best Params: {grid.best_params_}\n")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model = best_tuned_model

    print("="*60)
    print(f"🥇 GRAND CHAMPION: {best_model_name} with {best_accuracy * 100:.2f}%")
    print("="*60 + "\n")
    
    # 8. Save the Winning Model and Scaler
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(best_model, os.path.join(model_dir, 'rf_medguard_model.pkl')) # Keep original name for backend
    joblib.dump(le, os.path.join(model_dir, 'label_encoder.pkl'))
    joblib.dump(scaler, os.path.join(model_dir, 'scaler.pkl'))
    
    print(f"💾 Winning Model & Scaler safely locked for backend integration!")
    print("✅ ANALYSIS COMPLETE.")

# --- RUN THE SCRIPT ---
input_data = 'data/processed/ml_training_data.csv'
models_folder = 'models/'

if __name__ == "__main__":
    run_comparative_analysis(input_data, models_folder)