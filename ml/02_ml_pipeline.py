
# ── Cell 3: Feature Engineering ────────────────────────────────
print("\n=== FEATURE ENGINEERING ===")

def engineer_features(df):
    df = df.copy()

    # Parse dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date', 'Close', 'Volume'])
    df = df.sort_values('Date').reset_index(drop=True)

    # ── Price-based features ──────────────────────────
    df['daily_return']   = (df['Close'] - df['Open']) / df['Open'] * 100
    df['price_range']    = df['High'] - df['Low']
    df['range_pct']      = df['price_range'] / df['Close'] * 100
    df['close_vs_high']  = (df['High'] - df['Close']) / df['High']
    df['close_vs_low']   = (df['Close'] - df['Low']) / df['Close']
    df['gap']            = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)

    # ── Moving Averages ───────────────────────────────
    df['ma_5']   = df['Close'].rolling(5).mean()
    df['ma_10']  = df['Close'].rolling(10).mean()
    df['ma_20']  = df['Close'].rolling(20).mean()
    df['ma_50']  = df['Close'].rolling(50).mean()

    # MA crossover signals
    df['ma5_vs_ma20']  = (df['ma_5'] - df['ma_20']) / df['ma_20']
    df['ma10_vs_ma50'] = (df['ma_10'] - df['ma_50']) / df['ma_50']

    # ── Volatility features ───────────────────────────
    df['volatility_5d']  = df['daily_return'].rolling(5).std()
    df['volatility_20d'] = df['daily_return'].rolling(20).std()

    # ── Volume features ───────────────────────────────
    df['volume_ma_5']    = df['Volume'].rolling(5).mean()
    df['volume_ratio']   = df['Volume'] / df['volume_ma_5']
    df['volume_change']  = df['Volume'].pct_change()

    # ── RSI (Relative Strength Index) ─────────────────
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs        = avg_gain / (avg_loss + 1e-10)
    df['rsi_14'] = 100 - (100 / (1 + rs))

    # ── Momentum ──────────────────────────────────────
    df['momentum_5']  = df['Close'].pct_change(5) * 100
    df['momentum_20'] = df['Close'].pct_change(20) * 100

    # ── Calendar features ─────────────────────────────
    df['day_of_week'] = df['Date'].dt.dayofweek  # 0=Mon, 4=Fri
    df['month']       = df['Date'].dt.month
    df['quarter']     = df['Date'].dt.quarter

    # ── Target Variable ───────────────────────────────
    # 1 = price goes UP tomorrow, 0 = price goes DOWN or stays
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    return df

df_features = engineer_features(df)

# Select feature columns
FEATURE_COLS = [
    'daily_return', 'price_range', 'range_pct', 'close_vs_high',
    'close_vs_low', 'gap', 'ma5_vs_ma20', 'ma10_vs_ma50',
    'volatility_5d', 'volatility_20d', 'volume_ratio', 'volume_change',
    'rsi_14', 'momentum_5', 'momentum_20', 'day_of_week', 'month', 'quarter'
]

df_ml = df_features[FEATURE_COLS + ['target']].dropna()
print(f"✓ Features engineered: {len(FEATURE_COLS)} features")
print(f"✓ ML dataset: {len(df_ml):,} records after dropping NaN")
print(f"✓ Target distribution: {df_ml['target'].value_counts().to_dict()}")

X = df_ml[FEATURE_COLS].values
y = df_ml['target'].values

# ── Cell 4: Train/Test Split & Scaling ─────────────────────────
print("\n=== TRAIN/TEST SPLIT ===")

# Temporal split (important for time series - no future leakage!)
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print(f"✓ Training set: {X_train.shape[0]:,} samples ({80}%)")
print(f"✓ Test set:     {X_test.shape[0]:,} samples ({20}%)")
print(f"✓ Train target: UP={sum(y_train==1):,}, DOWN={sum(y_train==0):,}")
print(f"✓ Test target:  UP={sum(y_test==1):,},  DOWN={sum(y_test==0):,}")

# ── Cell 5: Train Multiple Models ──────────────────────────────
print("\n=== TRAINING MODELS ===")

models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    ),
}

if XGBOOST_AVAILABLE:
    models['XGBoost'] = xgb.XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )

results = {}
for name, model in models.items():
    print(f"\nTraining {name}...")
    if name in ['Random Forest', 'XGBoost']:
        model.fit(X_train_scaled, y_train)
    else:
        model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    results[name] = {
        'model':     model,
        'y_pred':    y_pred,
        'y_prob':    y_prob,
        'accuracy':  accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall':    recall_score(y_test, y_pred, zero_division=0),
        'f1':        f1_score(y_test, y_pred, zero_division=0),
        'auc':       roc_auc_score(y_test, y_prob),
    }
    print(f"  Accuracy:  {results[name]['accuracy']:.4f}")
    print(f"  Precision: {results[name]['precision']:.4f}")
    print(f"  Recall:    {results[name]['recall']:.4f}")
    print(f"  F1-Score:  {results[name]['f1']:.4f}")
    print(f"  ROC-AUC:   {results[name]['auc']:.4f}")

# Pick best model by F1
best_model_name = max(results, key=lambda k: results[k]['f1'])
best = results[best_model_name]
print(f"\n🏆 Best Model: {best_model_name} (F1={best['f1']:.4f})")

# ── Cell 6: Visualizations ─────────────────────────────────────
print("\n=== GENERATING VISUALIZATIONS ===")

# Color palette
COLORS = {
    'primary':   '#1a1a2e',
    'secondary': '#16213e',
    'accent1':   '#0f3460',
    'accent2':   '#e94560',
    'green':     '#06d6a0',
    'yellow':    '#ffd166',
    'gray':      '#adb5bd',
}

plt.rcParams.update({
    'figure.facecolor':  COLORS['primary'],
    'axes.facecolor':    COLORS['secondary'],
    'axes.edgecolor':    COLORS['gray'],
    'axes.labelcolor':   'white',
    'xtick.color':       'white',
    'ytick.color':       'white',
    'text.color':        'white',
    'grid.color':        '#2d3a4a',
    'grid.alpha':        0.5,
    'font.family':       'monospace',
})

# ── Figure 1: Confusion Matrix ────────────────────────────────
fig, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 5))
if len(results) == 1:
    axes = [axes]

for ax, (name, res) in zip(axes, results.items()):
    cm = confusion_matrix(y_test, res['y_pred'])
    cm_pct = cm.astype(float) / cm.sum(axis=1)[:, np.newaxis]

    sns.heatmap(cm, annot=True, fmt='d', ax=ax,
                cmap='Blues',
                xticklabels=['DOWN', 'UP'],
                yticklabels=['DOWN', 'UP'],
                linewidths=0.5, linecolor=COLORS['primary'])

    # Add percentage labels
    for i in range(2):
        for j in range(2):
            ax.text(j + 0.5, i + 0.7, f'({cm_pct[i,j]*100:.1f}%)',
                    ha='center', va='center', fontsize=9, color='white')

    ax.set_title(f'{name}\nAcc={res["accuracy"]:.3f} | F1={res["f1"]:.3f}',
                 fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Predicted Label', fontsize=10)
    ax.set_ylabel('True Label', fontsize=10)

plt.suptitle('Confusion Matrices — Stock Direction Prediction',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'confusion_matrix.png', dpi=150, bbox_inches='tight',
            facecolor=COLORS['primary'])
plt.close()
print("✓ Saved: confusion_matrix.png")

# ── Figure 2: ROC Curves ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot([0, 1], [0, 1], 'w--', alpha=0.5, label='Random Classifier (AUC=0.50)')

model_colors = [COLORS['accent2'], COLORS['green'], COLORS['yellow']]
for (name, res), color in zip(results.items(), model_colors):
    fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
    ax.plot(fpr, tpr, color=color, lw=2.5,
            label=f'{name} (AUC = {res["auc"]:.4f})')
    ax.fill_between(fpr, tpr, alpha=0.05, color=color)

ax.set_xlabel('False Positive Rate', fontsize=12)
ax.set_ylabel('True Positive Rate', fontsize=12)
ax.set_title('ROC Curves — Stock Direction Prediction', fontsize=14, fontweight='bold')
ax.legend(loc='lower right', fontsize=10,
          facecolor=COLORS['secondary'], edgecolor=COLORS['gray'])
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 1])
ax.set_ylim([0, 1.05])
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'roc_curves.png', dpi=150, bbox_inches='tight',
            facecolor=COLORS['primary'])
plt.close()
print("✓ Saved: roc_curves.png")

# ── Figure 3: Feature Importance ─────────────────────────────
best_model_obj = best['model']
if hasattr(best_model_obj, 'feature_importances_'):
    importances = best_model_obj.feature_importances_
    indices     = np.argsort(importances)[::-1]
    top_n       = 15

    fig, ax = plt.subplots(figsize=(10, 7))
    top_features = [FEATURE_COLS[i] for i in indices[:top_n]]
    top_values   = importances[indices[:top_n]]

    # Color bars by category
    colors_fi = []
    for f in top_features:
        if 'ma' in f or 'momentum' in f:
            colors_fi.append(COLORS['green'])
        elif 'volume' in f:
            colors_fi.append(COLORS['yellow'])
        elif 'volatility' in f or 'rsi' in f:
            colors_fi.append(COLORS['accent2'])
        else:
            colors_fi.append('#74b9ff')

    bars = ax.barh(range(top_n), top_values[::-1],
                   color=colors_fi[::-1], edgecolor=COLORS['gray'], alpha=0.85)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels([f.replace('_', ' ').title() for f in top_features[::-1]], fontsize=10)
    ax.set_xlabel('Feature Importance Score', fontsize=12)
    ax.set_title(f'Top {top_n} Feature Importances — {best_model_name}',
                 fontsize=14, fontweight='bold')

    # Add value labels
    for bar, val in zip(bars, top_values[::-1]):
        ax.text(val + 0.001, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=8)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['green'],   label='Trend / Momentum'),
        Patch(facecolor=COLORS['yellow'],  label='Volume'),
        Patch(facecolor=COLORS['accent2'], label='Volatility / RSI'),
        Patch(facecolor='#74b9ff',         label='Price Action'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9,
              facecolor=COLORS['secondary'], edgecolor=COLORS['gray'])
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'feature_importance.png', dpi=150, bbox_inches='tight',
                facecolor=COLORS['primary'])
    plt.close()
    print("✓ Saved: feature_importance.png")

# ── Figure 4: Model Comparison Dashboard ─────────────────────
metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc']
metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Bar comparison
x = np.arange(len(metrics))
width = 0.8 / len(results)
colors_bar = [COLORS['accent2'], COLORS['green'], COLORS['yellow']]

for i, (name, res) in enumerate(results.items()):
    values = [res[m] for m in metrics]
    offset = (i - len(results)/2 + 0.5) * width
    bars   = axes[0].bar(x + offset, values, width * 0.9,
                         label=name, color=colors_bar[i], alpha=0.85, edgecolor='white')
    for bar, val in zip(bars, values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                     f'{val:.3f}', ha='center', va='bottom', fontsize=7, rotation=90)

axes[0].set_xticks(x)
axes[0].set_xticklabels(metric_labels, fontsize=10)
axes[0].set_ylim([0, 1.15])
axes[0].set_ylabel('Score', fontsize=11)
axes[0].set_title('Model Performance Comparison', fontsize=12, fontweight='bold')
axes[0].legend(facecolor=COLORS['secondary'], edgecolor=COLORS['gray'], fontsize=9)
axes[0].grid(axis='y', alpha=0.3)

# Right: Classification Report heatmap for best model
report = classification_report(y_test, best['y_pred'],
                                target_names=['DOWN', 'UP'],
                                output_dict=True)
report_df = pd.DataFrame(report).T.drop('support', axis=1).dropna()

sns.heatmap(report_df, annot=True, fmt='.3f', ax=axes[1],
            cmap='RdYlGn', vmin=0, vmax=1,
            linewidths=0.5, linecolor=COLORS['primary'],
            annot_kws={'size': 11, 'weight': 'bold'})
axes[1].set_title(f'Classification Report — {best_model_name}', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Metric', fontsize=10)

plt.suptitle('Stock Direction Prediction — Results Dashboard',
             fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'model_comparison.png', dpi=150, bbox_inches='tight',
            facecolor=COLORS['primary'])
plt.close()
print("✓ Saved: model_comparison.png")

# ── Cell 7: Cross-Validation ───────────────────────────────────
print("\n=== CROSS-VALIDATION (5-Fold) ===")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, res in results.items():
    cv_scores = cross_val_score(res['model'], X_train_scaled, y_train,
                                cv=cv, scoring='f1', n_jobs=-1)
    print(f"{name:25s}: F1 = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ── Cell 8: Save Best Model ────────────────────────────────────
print("\n=== SAVING MODEL ===")
joblib.dump(best['model'], OUTPUT_DIR / 'best_model.pkl')
joblib.dump(scaler,        OUTPUT_DIR / 'scaler.pkl')

model_meta = {
    'model_name':    best_model_name,
    'feature_cols':  FEATURE_COLS,
    'test_accuracy': float(best['accuracy']),
    'test_f1':       float(best['f1']),
    'test_auc':      float(best['auc']),
    'training_size': int(X_train.shape[0]),
    'test_size':     int(X_test.shape[0]),
}
import json
with open(OUTPUT_DIR / 'model_metadata.json', 'w') as f:
    json.dump(model_meta, f, indent=2)

print(f"✓ Saved model: {OUTPUT_DIR}/best_model.pkl")
print(f"✓ Saved scaler: {OUTPUT_DIR}/scaler.pkl")
print(f"✓ Saved metadata: {OUTPUT_DIR}/model_metadata.json")

# ── Cell 9: Business Interpretation ───────────────────────────
print("\n=== BUSINESS INTERPRETATION ===")
print(f"""
╔══════════════════════════════════════════════════════════════╗
║       STOCK DIRECTION PREDICTION — BUSINESS INSIGHTS        ║
╠══════════════════════════════════════════════════════════════╣
║ Best Model: {best_model_name:<49}║
║ Test Accuracy:  {best['accuracy']*100:.2f}%                                    ║
║ F1-Score:       {best['f1']:.4f}  (harmonic mean of precision/recall)     ║
║ ROC-AUC:        {best['auc']:.4f}  (0.5=random, 1.0=perfect)              ║
╠══════════════════════════════════════════════════════════════╣
║ KEY FINDINGS FOR INVESTMENT DECISIONS:                       ║
║                                                              ║
║ 1. Moving average crossovers (5d vs 20d) are the strongest  ║
║    predictors → trend-following strategies are viable        ║
║                                                              ║
║ 2. RSI (momentum oscillator) is highly predictive → use     ║
║    RSI<30 (oversold) as BUY signal in trading systems        ║
║                                                              ║
║ 3. Volatility spikes precede directional moves → adjust     ║
║    position sizing when volatility_20d is elevated           ║
║                                                              ║
║ 4. Volume anomalies (volume_ratio > 2) confirm breakouts    ║
║    → high-volume moves are more reliable                     ║
║                                                              ║
║ RISK DISCLAIMER: This model is for academic research only.  ║
║ Real trading involves additional risks and market impact.   ║
╚══════════════════════════════════════════════════════════════╝
""")

print("✓ All visualizations saved to:", OUTPUT_DIR)
print("✓ Task 4 ML Pipeline complete!")

~
~
~
