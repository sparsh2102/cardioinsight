import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, roc_auc_score)
import pickle, os

df = pd.read_csv('heart_data.csv')

FEATURES = ['age', 'sex', 'trestbps', 'chol', 'thalach', 'smoking', 'exercise', 'exang', 'ca']
X = df[FEATURES]
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200, max_depth=10,
                                min_samples_split=5, random_state=42, n_jobs=-1)
model.fit(X_train_s, y_train)

y_pred = model.predict(X_test_s)
y_prob = model.predict_proba(X_test_s)[:, 1]

acc      = accuracy_score(y_test, y_pred)
auc      = roc_auc_score(y_test, y_prob)
cm       = confusion_matrix(y_test, y_pred)
report   = classification_report(y_test, y_pred)

print(f"\n{'='*50}")
print(f"  MODEL TRAINING COMPLETE")
print(f"{'='*50}")
print(f"  Accuracy  : {acc*100:.2f}%")
print(f"  AUC-ROC   : {auc:.4f}")
print(f"\nClassification Report:\n{report}")
print(f"Confusion Matrix:\n{cm}")

os.makedirs('models', exist_ok=True)
pickle.dump(model,  open('models/rf_model.pkl',  'wb'))
pickle.dump(scaler, open('models/scaler.pkl',    'wb'))

# Save metrics for display
metrics = {
    'accuracy':  round(acc * 100, 2),
    'auc':       round(auc, 4),
    'features':  FEATURES,
    'train_size': len(X_train),
    'test_size':  len(X_test),
    'cm':         cm.tolist(),
    'report':     report
}
import json
json.dump(metrics, open('models/metrics.json', 'w'))
print("\nModel saved to models/")
