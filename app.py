from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from database import (init_db, register_user, login_user, save_assessment, get_user_assessments, get_user_by_id, update_user_name, update_user_password, clear_user_history, get_user_risk_stats, get_admin_stats, get_all_assessments, get_all_users)
from werkzeug.security import check_password_hash
from predictor import predict_risk, get_label_color, get_metrics, get_recommendations
from charts import generate_all
from pdf_generator import generate_report
import os, json

app = Flask(__name__)
app.secret_key = 'cardioinsight_secret_2024'

# ── Init ──────────────────────────────────────────────────────
init_db()
generate_all()

# ── Helpers ───────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def validate_inputs(age, chol, bp, hr):
    errors = []
    if not (18 <= age <= 120):
        errors.append("Age must be between 18 and 120.")
    if not (100 <= chol <= 600):
        errors.append("Cholesterol must be between 100 and 600 mg/dl.")
    if not (60 <= bp <= 250):
        errors.append("Blood pressure must be between 60 and 250 mmHg.")
    if not (40 <= hr <= 250):
        errors.append("Heart rate must be between 40 and 250 bpm.")
    return errors

# ── Routes ────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name  = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','')
        pw2   = request.form.get('confirm_password','')

        if not all([name, email, pw]):
            flash('All fields are required.', 'error')
        elif len(pw) < 6:
            flash('Password must be at least 6 characters.', 'error')
        elif pw != pw2:
            flash('Passwords do not match.', 'error')
        else:
            ok, msg = register_user(name, email, pw)
            if ok:
                flash('Account created! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash(msg, 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','')
        ok, result = login_user(email, pw)
        if ok:
            session['user_id'] = result['id']
            session['user_name'] = result['name']
            flash(f'Welcome back, {result["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result, 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/assessment')
@login_required
def assessment():
    return render_template('assessment.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        name     = request.form.get('name','').strip() or session['user_name']
        age      = int(request.form['age'])
        sex      = int(request.form['sex'])
        chol     = int(request.form['cholesterol'])
        bp       = int(request.form['bp'])
        hr       = int(request.form['heart_rate'])
        smoking  = int(request.form['smoking'])
        exercise = int(request.form['exercise'])
        exang    = int(request.form['exang'])
        ca       = int(request.form['ca'])

        errors = validate_inputs(age, chol, bp, hr)
        if errors:
            for e in errors:
                flash(e, 'error')
            return redirect(url_for('assessment'))

        risk  = predict_risk(age, sex, bp, chol, hr, smoking, exercise, exang, ca)
        label, color = get_label_color(risk)
        recs  = get_recommendations(risk, smoking, exercise, chol, bp, age)

        save_assessment(session['user_id'], name, age, sex, chol, bp, hr,
                        smoking, exercise, exang, ca, risk, label)

        pdf_path = generate_report(name, age, sex, chol, bp, hr,
                                   smoking, exercise, exang, ca, risk, label, recs)

        return render_template('report.html',
            name=name, age=age, sex=sex, chol=chol, bp=bp, hr=hr,
            smoking=smoking, exercise=exercise, risk=risk,
            label=label, color=color, recs=recs,
            pdf_filename=os.path.basename(pdf_path)
        )
    except (ValueError, KeyError) as e:
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('assessment'))

@app.route('/download/<filename>')
@login_required
def download(filename):
    safe = filename.replace('/', '').replace('\\', '').replace('..', '')
    path = os.path.join('static', 'reports', safe)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    flash('Report not found.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    user      = get_user_by_id(session['user_id'])
    history   = get_user_assessments(session['user_id'])
    metrics   = get_metrics()
    return render_template('dashboard.html',
        user=user, history=history, metrics=metrics)

@app.route('/analytics')
@login_required
def analytics():
    import pandas as pd
    df = pd.read_csv('heart_data.csv')
    stats = {
        'total_records':  len(df),
        'avg_age':        round(df['age'].mean(), 1),
        'high_chol_pct':  round((df['chol'] > 200).mean() * 100, 1),
        'high_bp_pct':    round((df['trestbps'] > 130).mean() * 100, 1),
        'disease_pct':    round(df['target'].mean() * 100, 1),
        'smoker_pct':     round(df['smoking'].mean() * 100, 1),
    }
    metrics = get_metrics()
    return render_template('analytics.html', stats=stats, metrics=metrics)

@app.route('/library')
def library():
    diseases = [
        {
            'name': 'Coronary Artery Disease',
            'icon': '🫀',
            'desc': 'Narrowing of coronary arteries due to plaque buildup, reducing blood flow to the heart.',
            'symptoms': ['Chest pain (angina)', 'Shortness of breath', 'Fatigue', 'Heart attack'],
            'prevention': ['Exercise regularly', 'Healthy diet', 'Quit smoking', 'Manage cholesterol'],
            'color': '#e74c3c'
        },
        {
            'name': 'Heart Failure',
            'icon': '💔',
            'desc': 'The heart cannot pump enough blood to meet the body\'s needs.',
            'symptoms': ['Breathlessness', 'Swollen legs/ankles', 'Persistent fatigue', 'Rapid heartbeat'],
            'prevention': ['Control blood pressure', 'Avoid alcohol', 'Maintain healthy weight', 'Monitor sodium'],
            'color': '#9b59b6'
        },
        {
            'name': 'Arrhythmia',
            'icon': '⚡',
            'desc': 'Irregular heartbeat — the heart beats too fast, too slow, or irregularly.',
            'symptoms': ['Palpitations', 'Dizziness', 'Fainting', 'Chest discomfort'],
            'prevention': ['Limit caffeine', 'Reduce stress', 'Control electrolytes', 'Avoid stimulants'],
            'color': '#f39c12'
        },
        {
            'name': 'Hypertension',
            'icon': '📈',
            'desc': 'High blood pressure — a major risk factor for heart disease and stroke.',
            'symptoms': ['Often no symptoms', 'Headaches', 'Nosebleeds', 'Dizziness'],
            'prevention': ['Low-salt diet', 'Regular exercise', 'Maintain healthy weight', 'Limit alcohol'],
            'color': '#e67e22'
        },
        {
            'name': 'Stroke',
            'icon': '🧠',
            'desc': 'Blockage or rupture of blood supply to the brain, often linked to heart conditions.',
            'symptoms': ['Sudden numbness', 'Confusion', 'Vision problems', 'Severe headache'],
            'prevention': ['Control BP & cholesterol', 'Exercise', 'Healthy diet', 'No smoking'],
            'color': '#3498db'
        },
        {
            'name': 'Atherosclerosis',
            'icon': '🔴',
            'desc': 'Hardening and narrowing of arteries due to fatty deposits (plaques).',
            'symptoms': ['Chest pain', 'Leg pain when walking', 'Shortness of breath', 'Fatigue'],
            'prevention': ['Heart-healthy diet', 'Exercise', 'Quit smoking', 'Manage diabetes'],
            'color': '#1abc9c'
        },
    ]
    return render_template('library.html', diseases=diseases)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# ── Profile routes ────────────────────────────────────────────
@app.route('/profile')
@login_required
def profile():
    user    = get_user_by_id(session['user_id'])
    rstats  = get_user_risk_stats(session['user_id'])
    return render_template('profile.html',
        user=user,
        total_assessments=rstats['total'],
        avg_risk=rstats['avg_risk']
    )

@app.route('/profile/update-name', methods=['POST'])
@login_required
def update_name():
    new_name = request.form.get('name', '').strip()
    if not new_name:
        flash('Name cannot be empty.', 'error')
    else:
        update_user_name(session['user_id'], new_name)
        session['user_name'] = new_name
        flash('Name updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current = request.form.get('current_password', '')
    new_pw  = request.form.get('new_password', '')
    confirm = request.form.get('confirm_password', '')
    user    = get_user_by_id(session['user_id'])

    if not check_password_hash(user['password'], current):
        flash('Current password is incorrect.', 'error')
    elif len(new_pw) < 6:
        flash('New password must be at least 6 characters.', 'error')
    elif new_pw != confirm:
        flash('New passwords do not match.', 'error')
    else:
        update_user_password(session['user_id'], new_pw)
        flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/clear-history', methods=['POST'])
@login_required
def delete_history():
    clear_user_history(session['user_id'])
    flash('All assessment history deleted.', 'info')
    return redirect(url_for('dashboard'))

# ── Admin routes ──────────────────────────────────────────────
ADMIN_EMAIL = 'admin@cardioinsight.com'

@app.route('/admin')
@login_required
def admin():
    user = get_user_by_id(session['user_id'])
    if user['email'] != ADMIN_EMAIL:
        flash('Admin access required.', 'error')
        return redirect(url_for('dashboard'))
    stats       = get_admin_stats()
    assessments = get_all_assessments(50)
    users       = get_all_users()
    return render_template('admin.html', stats=stats, assessments=assessments, users=users)

# ── Error handlers ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
