"""
Generate charts and Word document for Pessoa 5 – Statistical Validation / Modeling / Robustness
Mountain Wellness Retreat – Guarda vs Vila Real
"""

import warnings
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor, Cm
from docx import Document
from scipy import stats
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────
# COLOUR PALETTE (matches project style)
# ──────────────────────────────────────────────
C_GUARDA = '#2C7BB6'   # blue
C_VILAREAL = '#D7191C'   # red/orange

FONT = 'DejaVu Sans'
plt.rcParams.update({
    'font.family': FONT,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────
# DATA USED (extracted from milestone2_completo.tex)
# ──────────────────────────────────────────────

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
months_num = list(range(1, 13))

# Mean temperature by month
mean_temp_guarda = [5.2,  6.1,  9.2, 11.8, 15.4,
                    19.5, 22.3, 22.1, 18.2, 13.1, 8.4,  5.6]
mean_temp_vilareal = [7.9,  9.0, 12.0, 14.3,
                      17.9, 22.4, 25.4, 25.2, 21.2, 15.8, 11.0, 8.3]

# Mean max temp by season [Winter, Spring, Summer, Autumn]
max_temp_season_g = [9.5,  16.0, 25.8, 17.8]
max_temp_season_vr = [12.1, 18.5, 27.3, 20.5]
seasons = ['Winter', 'Spring', 'Summer', 'Autumn']

# OK days by season (total across 2018-2026)
ok_days_season_g = [0,   140, 276, 207]
ok_days_season_vr = [9,   182, 211, 210]

# Annual OK days per year (2018-2025)
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
ok_days_annual_g = [96,  67,  82,  84,  79,  76,  73,  83]
ok_days_annual_vr = [83,  70,  72,  73,  57,  90,  98,  76]

# Extreme event frequencies (% of total days)
extreme_labels = ['Freezing days\n(min < 0°C)', 'Hot days\n(max > 30°C)',
                  'Warm nights\n(min > 20°C)', 'Rain days\n(≥1mm)']
extreme_pct_g = [10.9, 5.3,  0.5, 28.7]
extreme_pct_vr = [2.2,  9.1,  2.5, 34.9]

# Annual consistency – key indicators
annual_indicators = ['OK days', 'Freezing days',
                     'Hot days\n(>30°C)', 'Rain days', 'Precipitation\n(mm/yr)']
mean_g = [77.9, 38.6, 19.9, 102.8, 809]
cv_g = [13.5, 25.0, 59.5,   7.5, 16.2]
mean_vr = [76.0,  8.0, 33.8, 124.8, 1372]
cv_vr = [18.0, 70.7, 48.3,   5.4,  9.8]

# Test & Score results
classifiers = ['Decision Tree\n(depth 5)',
               'Naive Bayes', 'Logistic\nRegression']
auc_vals = [0.899, 0.857, 0.845]
ca_vals = [0.841, 0.782, 0.787]
f1_vals = [0.695, 0.621, 0.369]
rec_vals = [0.871, 0.864, 0.302]
prec_vals = [0.579, 0.486, 0.478]

# Monthly CV of mean temperature (inter-annual)
cv_monthly_g = [28.7, 29.3, 18.5, 14.2, 10.8,
                8.3,  9.9,  5.4,  8.9, 13.5, 18.2, 25.0]
cv_monthly_vr = [12.9, 18.4, 13.0, 10.5,  8.3,
                 7.1,  9.0,  6.1,  7.5, 10.2, 12.8, 15.6]

# Student t-test values from the text
# Precipitation: t=8.330, p=0.000
# Sunshine: t=2.889, p=0.004
# Cloud cover: t=3.304, p=0.001

# Cohen's d (approximate, computed from means/stds in the text)
# Precipitation: Guarda mean=2.31 std=5.78; VR mean=3.93 std=8.88
# Sunshine: Guarda 9.12 std=3.87; VR 8.82 std=4.10
# Cloud cover: Guarda 51.2 std=33.78; VR 54.1 std=34.30


# ──────────────────────────────────────────────
# CHART 1 – t-test & Effect Size summary bar
# ──────────────────────────────────────────────
def fig1_statistical_tests():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # ---- Left: t-statistics ----
    ax = axes[0]
    variables = ['Precipitation', 'Cloud Cover', 'Sunshine\nDuration']
    t_vals = [8.330, 3.304, 2.889]
    p_vals = [0.000, 0.001, 0.004]

    colors = ['#1a6fb3', '#1a6fb3', '#1a6fb3']
    bars = ax.barh(variables, t_vals, color=colors,
                   edgecolor='white', height=0.5)
    ax.axvline(1.96, color='crimson', linestyle='--',
               linewidth=1.5, label='Critical value (α=0.05)')
    for i, (b, p) in enumerate(zip(bars, p_vals)):
        label = f't = {t_vals[i]:.3f},  p < {p+0.001:.3f}'
        ax.text(b.get_width() + 0.1, b.get_y() + b.get_height()/2,
                label, va='center', ha='left', fontsize=9)
    ax.set_xlabel('Student\'s t-statistic', fontsize=11)
    ax.set_title('Independent Samples t-Tests\n(Guarda vs Vila Real, N = 5,962)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.set_xlim(0, 11.5)

    # ---- Right: Cohen's d (effect size) ----
    ax2 = axes[1]
    # pooled std approximation
    # precipitation: pooled_std = sqrt((5.78**2+8.88**2)/2) ≈ 7.49
    # sunshine: pooled_std ≈ 3.99  cloud: pooled_std ≈ 34.04
    d_vals = [
        abs(2.31 - 3.93) / np.sqrt((5.78**2 + 8.88**2)/2),   # precipitation
        abs(51.2 - 54.1) / np.sqrt((33.78**2 + 34.30**2)/2),  # cloud cover
        abs(9.12 - 8.82) / np.sqrt((3.87**2 + 4.10**2)/2),   # sunshine
    ]
    d_labels = ['Precipitation', 'Cloud Cover', 'Sunshine\nDuration']
    bar_colors = ['#2C7BB6' if d > 0.2 else '#aaa' for d in d_vals]
    brs = ax2.barh(d_labels, d_vals, color=bar_colors,
                   edgecolor='white', height=0.5)
    ax2.axvline(0.2, color='orange',  linestyle='--',
                linewidth=1.5, label='Small effect (d=0.2)')
    ax2.axvline(0.5, color='crimson', linestyle='--',
                linewidth=1.5, label='Medium effect (d=0.5)')
    for b, d in zip(brs, d_vals):
        ax2.text(b.get_width() + 0.005, b.get_y() + b.get_height()/2,
                 f'd = {d:.3f}', va='center', ha='left', fontsize=9)
    ax2.set_xlabel("Cohen's d (effect size)", fontsize=11)
    ax2.set_title("Effect Size Estimation\n(Cohen's d, pooled SD)",
                  fontsize=11, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.set_xlim(0, 0.45)

    plt.tight_layout(pad=2)
    path = os.path.join(OUTPUT_DIR, 'stat_tests_effect_size.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


# ──────────────────────────────────────────────
# CHART 2 – Annual CV of key indicators
# ──────────────────────────────────────────────
def fig2_annual_cv():
    ind = np.arange(len(annual_indicators))
    width = 0.35
    fig, ax = plt.subplots(figsize=(11, 5.5))

    b1 = ax.bar(ind - width/2, cv_g,  width, label='Guarda',
                color=C_GUARDA,   alpha=0.88, edgecolor='white')
    b2 = ax.bar(ind + width/2, cv_vr, width, label='Vila Real',
                color=C_VILAREAL, alpha=0.88, edgecolor='white')

    for b in [b1, b2]:
        for rect in b:
            h = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2, h + 0.5,
                    f'{h:.1f}%', ha='center', va='bottom', fontsize=8.5)

    ax.set_xticks(ind)
    ax.set_xticklabels(annual_indicators, fontsize=10)
    ax.set_ylabel('Coefficient of Variation (%)', fontsize=11)
    ax.set_title('Inter-Annual Coefficient of Variation — Key Indicators\n(2018–2025, lower = more predictable)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0, max(max(cv_g), max(cv_vr)) * 1.25)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'annual_cv_indicators.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


# ──────────────────────────────────────────────
# CHART 3 – Monthly inter-annual temperature CV
# ──────────────────────────────────────────────
def fig3_monthly_cv():
    fig, ax = plt.subplots(figsize=(11, 5))

    x = np.arange(12)
    ax.plot(x, cv_monthly_g,  marker='o', color=C_GUARDA,
            linewidth=2.2, markersize=7, label='Guarda')
    ax.plot(x, cv_monthly_vr, marker='s', color=C_VILAREAL,
            linewidth=2.2, markersize=7, label='Vila Real')
    ax.fill_between(x, cv_monthly_g, cv_monthly_vr,
                    where=[g > v for g, v in zip(cv_monthly_g, cv_monthly_vr)],
                    alpha=0.12, color=C_GUARDA, label='Guarda more variable')

    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=10)
    ax.set_ylabel('Inter-Annual CV of Mean Temperature (%)', fontsize=11)
    ax.set_title('Monthly Inter-Annual Temperature Variability (CV %)\n'
                 'Guarda vs Vila Real — Calendar Month Profile', fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0, 35)

    # shade summer
    ax.axvspan(4.5, 7.5, alpha=0.06, color='gold', label='Summer months')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'monthly_cv_temperature.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


# ──────────────────────────────────────────────
# CHART 4 – Extreme event frequencies (%)
# ──────────────────────────────────────────────
def fig4_extreme_freq():
    ind = np.arange(len(extreme_labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(11, 5.5))

    b1 = ax.bar(ind - width/2, extreme_pct_g,  width, label='Guarda',
                color=C_GUARDA,   alpha=0.88, edgecolor='white')
    b2 = ax.bar(ind + width/2, extreme_pct_vr, width, label='Vila Real',
                color=C_VILAREAL, alpha=0.88, edgecolor='white')

    for b in [b1, b2]:
        for rect in b:
            h = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2, h + 0.2,
                    f'{h:.1f}%', ha='center', va='bottom', fontsize=9)

    ax.set_xticks(ind)
    ax.set_xticklabels(extreme_labels, fontsize=10.5)
    ax.set_ylabel('% of Total Days', fontsize=11)
    ax.set_title('Frequency of Extreme Days — Guarda vs Vila Real\n(2018–early 2026, N = 2,981 days per location)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0, max(max(extreme_pct_g), max(extreme_pct_vr)) * 1.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'extreme_event_frequencies.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


# ──────────────────────────────────────────────
# CHART 5 – Test & Score model comparison
# ──────────────────────────────────────────────
def fig5_model_performance():
    metrics = ['AUC', 'Accuracy\n(CA)', 'F1', 'Precision', 'Recall']
    tree_vals = [0.899, 0.841, 0.695, 0.579, 0.871]
    nb_vals = [0.857, 0.782, 0.621, 0.486, 0.864]
    lr_vals = [0.845, 0.787, 0.369, 0.478, 0.302]

    x = np.arange(len(metrics))
    width = 0.25
    fig, ax = plt.subplots(figsize=(12, 5.5))

    b1 = ax.bar(x - width,       tree_vals, width,
                label='Decision Tree (depth 5)', color='#2C7BB6', edgecolor='white')
    b2 = ax.bar(x,               nb_vals,   width, label='Naive Bayes',
                color='#5BAD6F', edgecolor='white')
    b3 = ax.bar(x + width,       lr_vals,   width,
                label='Logistic Regression',     color='#E07A31', edgecolor='white')

    for b_group in [b1, b2, b3]:
        for rect in b_group:
            h = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2, h + 0.005,
                    f'{h:.3f}', ha='center', va='bottom', fontsize=7.5, rotation=0)

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.set_ylabel('Score', fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.axhline(0.5, color='grey', linestyle=':', linewidth=1,
               alpha=0.7, label='Chance level (0.5)')
    ax.set_title('Test & Score — 10-Fold Cross-Validation\nTarget: ok_day  |  Features: indirect atmospheric variables',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=9.5, loc='upper right')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'model_performance.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


# ──────────────────────────────────────────────
# CHART 6 – Annual OK days with mean lines
# ──────────────────────────────────────────────
def fig6_annual_ok_days():
    x = np.arange(len(years))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 5.5))

    b1 = ax.bar(x - width/2, ok_days_annual_g,  width, label='Guarda',
                color=C_GUARDA,   alpha=0.85, edgecolor='white')
    b2 = ax.bar(x + width/2, ok_days_annual_vr, width, label='Vila Real',
                color=C_VILAREAL, alpha=0.85, edgecolor='white')

    mean_g_val = np.mean(ok_days_annual_g)
    mean_vr_val = np.mean(ok_days_annual_vr)
    ax.axhline(mean_g_val,  color=C_GUARDA,   linestyle='--', linewidth=1.8,
               label=f'Guarda mean = {mean_g_val:.1f} (CV={13.5}%)')
    ax.axhline(mean_vr_val, color=C_VILAREAL, linestyle='--', linewidth=1.8,
               label=f'Vila Real mean = {mean_vr_val:.1f} (CV={18.0}%)')

    for b in [b1, b2]:
        for rect in b:
            h = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2, h + 0.5,
                    str(int(h)), ha='center', va='bottom', fontsize=8.5)

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], fontsize=10)
    ax.set_ylabel('Total OK Days per Year', fontsize=11)
    ax.set_title('Annual OK Days with Inter-Annual Variability\n'
                 'Lower CV = more predictable year-to-year', fontsize=11, fontweight='bold')
    ax.legend(fontsize=9.5)
    ax.set_ylim(0, 130)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'annual_ok_days_cv.png')
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


# ──────────────────────────────────────────────
# GENERATE ALL FIGURES
# ──────────────────────────────────────────────
print('Generating figures...')
p1 = fig1_statistical_tests()
p2 = fig2_annual_cv()
p3 = fig3_monthly_cv()
p4 = fig4_extreme_freq()
p5 = fig5_model_performance()
p6 = fig6_annual_ok_days()
print('All figures done.')
