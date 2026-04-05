import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
import os, json

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': '#0f1117',
    'axes.facecolor': '#1a1d2e',
    'axes.labelcolor': '#e0e0e0',
    'xtick.color': '#aaaaaa',
    'ytick.color': '#aaaaaa',
    'text.color': '#e0e0e0',
    'grid.color': '#2a2d3e',
    'grid.linestyle': '--',
    'grid.alpha': 0.5,
})

CHART_DIR = 'static/charts'
os.makedirs(CHART_DIR, exist_ok=True)

def load_data():
    return pd.read_csv('heart_data.csv')

# ── Chart 1: Age Group Risk Bar Chart ─────────────────────────
def age_risk_chart():
    df = load_data()
    df['age_group'] = pd.cut(df['age'], bins=[20,30,40,50,60,70,80],
                              labels=['20-30','31-40','41-50','51-60','61-70','71-80'])
    risk = df.groupby('age_group', observed=True)['target'].mean() * 100

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#27ae60','#2ecc71','#f39c12','#e67e22','#e74c3c','#c0392b']
    bars = ax.bar(risk.index, risk.values, color=colors, edgecolor='none', width=0.6)

    for bar, val in zip(bars, risk.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_title('Heart Disease Risk by Age Group', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Age Group', fontsize=11)
    ax.set_ylabel('Risk Percentage (%)', fontsize=11)
    ax.set_ylim(0, 100)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/age_risk.png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

# ── Chart 2: Cholesterol Distribution ─────────────────────────
def cholesterol_chart():
    df = load_data()
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(df[df['target']==0]['chol'], bins=40, alpha=0.7, color='#27ae60', label='No Disease', edgecolor='none')
    ax.hist(df[df['target']==1]['chol'], bins=40, alpha=0.7, color='#e74c3c', label='Heart Disease', edgecolor='none')
    ax.axvline(200, color='#f39c12', linestyle='--', linewidth=2, label='Risk Threshold (200)')

    ax.set_title('Cholesterol Distribution by Disease Status', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Cholesterol (mg/dl)', fontsize=11)
    ax.set_ylabel('Number of Patients', fontsize=11)
    ax.legend(fontsize=10)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/cholesterol.png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

# ── Chart 3: Smoking Pie Chart ─────────────────────────────────
def smoking_chart():
    df = load_data()
    counts = df['smoking'].value_counts()
    labels = ['Non-Smokers', 'Smokers']
    colors = ['#27ae60', '#e74c3c']
    explode = (0.03, 0.07)

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        counts, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=90,
        explode=explode, shadow=True,
        textprops={'color': '#e0e0e0', 'fontsize': 12}
    )
    for at in autotexts:
        at.set_fontsize(13)
        at.set_fontweight('bold')

    ax.set_title('Smoking Distribution in Dataset', fontsize=14, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/smoking.png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

# ── Chart 4: BP vs Cholesterol Scatter ────────────────────────
def scatter_chart():
    df = load_data().sample(2000, random_state=42)
    fig, ax = plt.subplots(figsize=(10, 6))

    sc = ax.scatter(df['chol'], df['trestbps'],
                    c=df['target'], cmap='RdYlGn_r',
                    alpha=0.6, s=18, edgecolors='none')
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('Heart Disease (1=Yes)', fontsize=10)
    cbar.ax.yaxis.set_tick_params(color='#aaaaaa')

    ax.set_title('Cholesterol vs Blood Pressure', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Cholesterol (mg/dl)', fontsize=11)
    ax.set_ylabel('Blood Pressure (mmHg)', fontsize=11)
    ax.yaxis.grid(True)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/scatter.png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

# ── Chart 5: Correlation Heatmap ───────────────────────────────
def heatmap_chart():
    df = load_data()
    cols = ['age','trestbps','chol','thalach','smoking','exercise','target']
    rename = {'trestbps':'BP','thalach':'HeartRate','target':'Disease'}
    corr = df[cols].rename(columns=rename).corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                ax=ax, linewidths=0.5, linecolor='#0f1117',
                cbar_kws={'shrink': 0.8},
                annot_kws={'size': 10, 'color': 'white'})
    ax.set_title('Correlation Heatmap — Health Factors', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/heatmap.png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

# ── Chart 6: Exercise vs Risk ──────────────────────────────────
def exercise_chart():
    df = load_data()
    groups = df.groupby('exercise')['target'].mean() * 100
    labels = ['No Exercise', 'Exercises Regularly']
    colors = ['#e74c3c', '#27ae60']

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, groups.values, color=colors, width=0.4, edgecolor='none')
    for bar, val in zip(bars, groups.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_title('Exercise Habit vs Heart Disease Risk', fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Risk Percentage (%)', fontsize=11)
    ax.set_ylim(0, 100)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/exercise.png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

# ── Chart 7: Confusion Matrix ──────────────────────────────────
def confusion_matrix_chart():
    metrics = json.load(open('models/metrics.json'))
    cm = np.array(metrics['cm'])

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['No Disease','Disease'],
                yticklabels=['No Disease','Disease'],
                linewidths=1, linecolor='#0f1117',
                annot_kws={'size': 14, 'fontweight': 'bold'})
    ax.set_title('Model Confusion Matrix', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Predicted', fontsize=11)
    ax.set_ylabel('Actual', fontsize=11)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/confusion_matrix.png', dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

def generate_all():
    print("Generating charts...")
    age_risk_chart()
    cholesterol_chart()
    smoking_chart()
    scatter_chart()
    heatmap_chart()
    exercise_chart()
    confusion_matrix_chart()
    print("All charts saved.")

if __name__ == '__main__':
    generate_all()
