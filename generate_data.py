import pandas as pd
import numpy as np

np.random.seed(42)
n = 10000

age = np.random.randint(25, 80, n)
sex = np.random.randint(0, 2, n)
cp = np.random.randint(0, 4, n)
trestbps = np.random.randint(90, 200, n)
chol = np.random.randint(140, 400, n)
fbs = np.random.randint(0, 2, n)
restecg = np.random.randint(0, 3, n)
thalach = np.random.randint(70, 202, n)
exang = np.random.randint(0, 2, n)
smoking = np.random.randint(0, 2, n)
exercise = np.random.randint(0, 2, n)
oldpeak = np.round(np.random.uniform(0, 6, n), 1)
slope = np.random.randint(0, 3, n)
ca = np.random.randint(0, 4, n)

# Realistic target based on risk factors
risk_score = (
    (age > 55).astype(int) * 0.25 +
    (chol > 220).astype(int) * 0.20 +
    (trestbps > 130).astype(int) * 0.20 +
    smoking * 0.15 +
    (1 - exercise) * 0.10 +
    exang * 0.10
)
target = (risk_score + np.random.normal(0, 0.1, n) > 0.45).astype(int)

df = pd.DataFrame({
    'age': age, 'sex': sex, 'cp': cp,
    'trestbps': trestbps, 'chol': chol, 'fbs': fbs,
    'restecg': restecg, 'thalach': thalach, 'exang': exang,
    'smoking': smoking, 'exercise': exercise,
    'oldpeak': oldpeak, 'slope': slope, 'ca': ca,
    'target': target
})

df.to_csv('heart_data.csv', index=False)
print(f"Dataset created: {len(df)} records")
print(f"Heart disease cases: {df['target'].sum()} ({df['target'].mean()*100:.1f}%)")
print(f"Average age: {df['age'].mean():.1f}")
print(f"High cholesterol (>200): {(df['chol']>200).sum()} ({(df['chol']>200).mean()*100:.1f}%)")
print(f"High BP (>130): {(df['trestbps']>130).sum()} ({(df['trestbps']>130).mean()*100:.1f}%)")
