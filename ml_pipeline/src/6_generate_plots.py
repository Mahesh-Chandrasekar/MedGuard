import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_academic_chart():
    print("📊 Generating Thesis-Level Comparative Analysis Chart...")
    
    # These are the 4 models you are running
    models = ['Logistic Regression', 'SVM', 'Random Forest', 'XGBoost']
    
    # IMPORTANT: Update these 4 numbers with the exact percentages your 4_train_models.py script prints out!
    # I am using placeholder numbers here (e.g., 55.2, 60.1, etc.). Change them to your real results!
    accuracies = [55.2, 60.1, 75.4, 78.9] 
    
    # Create the visual plot
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Build the Bar Chart
    bars = sns.barplot(x=models, y=accuracies, palette="viridis")
    
    # Add titles and labels for the Thesis
    plt.title('MedGuard AI: Algorithm Comparative Analysis (Post-SMOTE)', fontsize=16, fontweight='bold', pad=15)
    plt.ylabel('Prediction Accuracy (%)', fontsize=12, fontweight='bold')
    plt.xlabel('Machine Learning Architecture', fontsize=12, fontweight='bold')
    plt.ylim(0, 100)
    
    # Put the exact percentage numbers on top of each bar
    for bar in bars.patches:
        bars.annotate(format(bar.get_height(), '.2f') + '%', 
                      (bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                      ha='center', va='center', size=12, xytext=(0, 8), 
                      textcoords='offset points', fontweight='bold')
    
    # Save the image
    os.makedirs('../reports/figures/', exist_ok=True)
    save_path = '../reports/figures/model_comparison.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    print(f"✅ Chart successfully saved to: {save_path}")
    plt.show()

# Run it
create_academic_chart()