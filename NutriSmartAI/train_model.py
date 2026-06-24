import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np

os.makedirs('ml', exist_ok=True)

print("=" * 60)
print("🧠 TRAINING ML MODEL WITH ALL DISEASES")
print("=" * 60)

# ============================================================
# STEP 1: CREATE TRAINING DATA
# ============================================================

all_diseases = ['Diabetes', 'Heart Disease', 'PCOS', 'Thyroid', 'BP', 'Cholesterol', 'Kidney Disease', 'Anemia', 'Gastric/Ulcer', 'None']
all_goals = ['Weight Loss', 'Weight Gain', 'Muscle Gain', 'Fitness Maintenance', 'Athlete Training']

# Diet mapping for each disease
disease_diet_map = {
    'Diabetes': 'Diabetes Diet',
    'Heart Disease': 'Heart Healthy Diet',
    'PCOS': 'PCOS Diet',
    'Thyroid': 'Thyroid Diet',
    'BP': 'Heart Healthy Diet',
    'Cholesterol': 'Heart Healthy Diet',
    'Kidney Disease': 'Kidney Diet',
    'Anemia': 'High Protein Diet',
    'Gastric/Ulcer': 'Balanced Diet',
    'None': None  # Will be handled separately
}

# Diet mapping for 'None' disease based on goal
goal_diet_map = {
    'Weight Loss': 'Low Calorie Diet',
    'Weight Gain': 'High Protein Diet',
    'Muscle Gain': 'High Protein Diet',
    'Fitness Maintenance': 'Balanced Diet',
    'Athlete Training': 'High Protein Diet'
}

print("\n📊 Creating dataset with all diseases...")

data = []
for disease in all_diseases:
    for goal in all_goals:
        # 30 samples per combination
        for _ in range(30):
            age = np.random.randint(18, 65)
            bmi = round(np.random.uniform(17, 35), 1)
            
            if disease == 'None':
                diet = goal_diet_map[goal]
            else:
                diet = disease_diet_map[disease]
            
            data.append([age, bmi, disease, goal, diet])

df = pd.DataFrame(data, columns=['age', 'bmi', 'disease', 'goal', 'diet_type'])
df.to_csv("dataset/diet_dataset.csv", index=False)
print(f"✅ Created {len(df)} training records")

# ============================================================
# STEP 2: TRAIN MODEL
# ============================================================

print("\n📊 Training model...")

# Load data
data = pd.read_csv("dataset/diet_dataset.csv")

# ✅ CRITICAL FIX: Replace any NaN with 'None'
data['disease'] = data['disease'].fillna('None')
data['goal'] = data['goal'].fillna('Fitness Maintenance')

# Encode
le_disease = LabelEncoder()
le_goal = LabelEncoder()
le_diet = LabelEncoder()

data['disease'] = le_disease.fit_transform(data['disease'])
data['goal'] = le_goal.fit_transform(data['goal'])
data['diet_type'] = le_diet.fit_transform(data['diet_type'])

X = data[['age', 'bmi', 'disease', 'goal']]
y = data['diet_type']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")

# ============================================================
# STEP 3: SAVE MODELS
# ============================================================

joblib.dump(model, "ml/diet_model.pkl")
joblib.dump(le_disease, "ml/le_disease.pkl")
joblib.dump(le_goal, "ml/le_goal.pkl")
joblib.dump(le_diet, "ml/le_diet.pkl")

print("\n✅ Models saved successfully!")

# ============================================================
# STEP 4: SHOW MAPPINGS
# ============================================================

print("\n" + "=" * 60)
print("📌 DISEASE → DIET MAPPING")
print("=" * 60)

for disease in all_diseases:
    if disease == 'None':
        print(f"\n{disease}:")
        for goal, diet in goal_diet_map.items():
            print(f"  → {goal} → {diet}")
    else:
        print(f"{disease} → {disease_diet_map[disease]}")

print("\n" + "=" * 60)
print("🧪 TESTING PREDICTIONS")
print("=" * 60)

test_cases = [
    ('Diabetes', 'Weight Loss'),
    ('Heart Disease', 'Fitness Maintenance'),
    ('PCOS', 'Weight Gain'),
    ('Thyroid', 'Muscle Gain'),
    ('BP', 'Weight Loss'),
    ('Cholesterol', 'Weight Gain'),
    ('Kidney Disease', 'Fitness Maintenance'),
    ('Anemia', 'Weight Loss'),
    ('Gastric/Ulcer', 'Muscle Gain'),
    ('None', 'Weight Loss'),
    ('None', 'Weight Gain'),
    ('None', 'Fitness Maintenance'),
]

for disease, goal in test_cases:
    try:
        d_enc = le_disease.transform([disease])[0]
        g_enc = le_goal.transform([goal])[0]
        pred = model.predict([[30, 22.0, d_enc, g_enc]])
        diet = le_diet.inverse_transform(pred)[0]
        print(f"✅ {disease:20} + {goal:20} → {diet}")
    except Exception as e:
        print(f"❌ {disease:20} + {goal:20} → Error: {e}")

print("\n" + "=" * 60)
print("🎉 TRAINING COMPLETE! Run: python app.py")
print("=" * 60)