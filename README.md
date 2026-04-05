# CardioInsight — Heart Disease Risk Assessment System

**By:** Satyam Kumar & Sparsh Goyal | BCA 3rd Year
**ML Accuracy:** 87.90% | **AUC-ROC:** 94.92% | **Records:** 10,000

## Quick Start
```bash
bash run.sh    # installs, trains model, starts server
```
Open: http://localhost:5000

## All Features
- ML Risk Prediction (Random Forest, 87.90% accuracy)
- User Register / Login / Logout (Werkzeug hashed passwords)
- 10-input validated Assessment Form
- Risk Score + Personalized Recommendations
- Downloadable PDF Report
- Assessment History per User
- Analytics Dashboard (7 charts)
- Disease Library (6 conditions)
- Profile Page (edit name, change password, delete history)
- Admin Panel (all users and assessments)
- 404 / 500 Error Pages
- Deployment Ready (Render.com / PythonAnywhere)

## Tech Stack
- Backend:   Python 3, Flask 3.0
- ML Model:  Scikit-learn RandomForestClassifier
- Analysis:  Pandas, NumPy
- Charts:    Matplotlib, Seaborn
- Database:  SQLite
- PDF:       FPDF2
- Auth:      Werkzeug
- Deploy:    Gunicorn + Render.com

## Routes (17 total)
GET  /                        Home page
GET  /register                Register form
POST /register                Create account
GET  /login                   Login form
POST /login                   Authenticate
GET  /logout                  Sign out
GET  /assessment              Health form (auth required)
POST /predict                 Run ML prediction (auth required)
GET  /download/<file>         Download PDF (auth required)
GET  /dashboard               History + model stats (auth required)
GET  /analytics               7 data charts (auth required)
GET  /library                 Disease library
GET  /profile                 Profile page (auth required)
POST /profile/update-name     Update name (auth required)
POST /profile/change-password Change password (auth required)
POST /profile/clear-history   Delete history (auth required)
GET  /admin                   Admin panel (admin email required)

## Admin Access
Register with: admin@cardioinsight.com
Then visit:    /admin

## ML Model
Algorithm  : Random Forest (200 trees, max depth 10)
Train/Test : 8000 / 2000 records
Accuracy   : 87.90%
AUC-ROC    : 94.92%

See DEPLOYMENT.md for hosting instructions.
